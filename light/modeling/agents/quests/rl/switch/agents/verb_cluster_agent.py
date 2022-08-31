# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from itertools import islice

from parlai.core.torch_agent import Output

from light.modeling.agents.quests.rl.shared.process.constants import *

from parlai.agents.transformer.biencoder import BiencoderAgent
from parlai.core.message import Message
from light.modeling.agents.quests.rl.shared.environments.history import (
    GoalOrientedHistory,
)


class VerbClusterAgent(BiencoderAgent):
    """
    Environment agent that both utters and acts/emotes. Initialized with
    fixed candidates but you can pass in candidates at inference time
    (for acts/emotes) and it will use those instead
    """

    def build_dictionary(self):
        """
        Return the constructed dictionary, which will be set to self.dict.

        If you need to add additional tokens to the dictionary, this is likely
        the right place to do it.
        """
        # Tokens shouldn't be added
        d = self.dictionary_class()(self.opt)
        return d

    @classmethod
    def history_class(cls):
        return GoalOrientedHistory

    def build_history(self):
        """
        Return the constructed history object.
        Use this to define your own P1/P2 tokens
        """
        return self.history_class()(
            self.opt,
            self.text_truncate,
            self.histsz,
            "_partner_say",
            "_self_say",
            self.dict,
            MISSING_SAY_TAG,
        )

    def block_repeats(self, cand_preds, batch):
        """Heuristic to block a model repeating a line from the history.
        Edited from TRA's block repeats
        """
        new_preds = []

        for cp, obs in zip(cand_preds, batch["observations"]):
            raw_history_strings = obs["full_text"].split("\n")
            history_strings = []
            for hs in raw_history_strings:
                sparts = hs.split(" ", 1)
                if len(sparts) > 0 and sparts[0] in ["_self_say", "_partner_say"]:
                    history_strings.append(sparts[1])
            np = []
            for c in cp:
                if c not in history_strings:
                    np.append(c)
            new_preds.append(np)
        return new_preds

    def observe(self, observation, self_observe=True):
        """
        Overrides the observe fn.
        Takes into account if the self response needs to be added to
        the history or not.
        """
        observation = Message(observation)
        if self_observe:
            reply = self.last_reply(use_reply=self.opt.get("use_reply", "label"))
            self.history.update_history(observation, add_next=reply)
        else:
            self.history.update_history(observation, add_next=None)
        self.observation = observation
        return self.vectorize(
            self.observation,
            self.history,
            text_truncate=self.text_truncate,
            label_truncate=self.label_truncate,
        )

    # def match_batch(self, batch_reply, valid_inds, output=None):
    #     batch_reply = super().match_batch(batch_reply, valid_inds, output)
    #
    #     if output.embedding_ctx is not None:
    #         for i, ectx, scores, cands, cand_hs, text in zip(
    #             valid_inds, output.embedding_ctx, output.scores, output.cands, output.cand_hs, output.text
    #         ):
    #             batch_reply[i]['embedding_ctx'] = ectx
    #             batch_reply[i]['scores'] = scores
    #             batch_reply[i]['cand_hs'] = cand_hs
    #             batch_reply[i]['cands'] = cands
    #             batch_reply[i]['text'] = text
    #     return batch_reply

    def match_batch(self, batch_reply, valid_inds, output=None):
        batch_reply = super().match_batch(batch_reply, valid_inds, output)
        if output.embedding_ctx is not None:
            for i, ectx, scores, cands, cand_hs in zip(
                valid_inds,
                output.embedding_ctx,
                output.scores,
                output.cands,
                output.cand_hs,
            ):
                batch_reply[i]["embedding_ctx"] = ectx
                batch_reply[i]["scores"] = scores
                batch_reply[i]["cand_hs"] = cand_hs
                batch_reply[i]["cands"] = cands
        return batch_reply

    def score_candidates(self, batch, cand_vecs, cand_encs=None):
        # convoluted check that not all memories are empty
        if (
            self.opt["use_memories"]
            and batch.memory_vecs is not None
            and sum(len(m) for m in batch.memory_vecs)
        ):
            mems = padded_3d(
                batch.memory_vecs, use_cuda=self.use_cuda, pad_idx=self.NULL_IDX
            )
        else:
            mems = None
        if cand_encs is not None and batch.candidate_vecs is None:
            # we pre-encoded the candidates, do not re-encode here
            cand_vecs = None

        context_h, cands_h = self.model(xs=batch.text_vec, mems=mems, cands=cand_vecs)
        if cand_encs is not None and batch.candidate_vecs is None:
            cands_h = cand_encs
        scores = self._score(context_h, cands_h)
        return scores, context_h

    def eval_step(self, batch):
        """Evaluate a single batch of examples."""
        # import pdb;pdb.set_trace()
        if batch.text_vec is None and batch.image is None:
            return
        batchsize = 1
        self.model.eval()

        cands, cand_vecs, _ = self._build_candidates(
            batch, source=self.eval_candidates, mode="eval"
        )

        cand_encs = None
        if self.encode_candidate_vecs:
            # if we cached candidate encodings for a fixed list of candidates,
            # pass those into the score_candidates function
            if self.eval_candidates == "fixed":
                cand_encs = self.fixed_candidate_encs
            elif self.eval_candidates == "vocab":
                cand_encs = self.vocab_candidate_encs

        scores, context_h = self.score_candidates(batch, cand_vecs, cand_encs=cand_encs)

        if self.rank_top_k > 0:
            _, ranks = scores.topk(
                min(self.rank_top_k, scores.size(1)), 1, largest=True
            )
        else:
            _, ranks = scores.sort(1, descending=True)

        ranks = ranks.cpu()
        max_preds = self.opt["cap_num_predictions"]
        cand_preds = []
        for i, ordering in enumerate(ranks):
            if cand_vecs.dim() == 2:
                cand_list = cands
            elif cand_vecs.dim() == 3:
                cand_list = cands[i]
            # using a generator instead of a list comprehension allows
            # to cap the number of elements.
            cand_preds_generator = (
                cand_list[rank] for rank in ordering if rank < len(cand_list)
            )
            cand_preds.append(list(islice(cand_preds_generator, max_preds)))

        if (
            self.opt.get("repeat_blocking_heuristic", True)
            and self.eval_candidates == "fixed"
        ):
            cand_preds = self.block_repeats(cand_preds, batch)

        preds = [cand_preds[i][0] for i in range(batchsize)]
        return Output(
            embedding_ctx=context_h,
            scores=scores,
            cands=[cands],
            cand_hs=cand_encs,
            text=preds,
        )
