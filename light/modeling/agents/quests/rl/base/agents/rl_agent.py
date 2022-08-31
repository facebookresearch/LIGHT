# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3
import torch
from itertools import islice

from parlai.core.torch_agent import Output
from light.modeling.agents.quests.rl.shared.process.constants import *
from light.modeling.agents.quests.rl.shared.models.transformer import (
    LightBiencoderAgent,
)
from light.modeling.agents.quests.rl.shared.environments.history import (
    GoalOrientedHistory,
)

from parlai.agents.bert_ranker.bi_encoder_ranker import BiEncoderRankerAgent
from parlai.agents.bert_ranker.bi_encoder_ranker import to_bert_input


class RLAgent(LightBiencoderAgent):
    """
    RLAgent is a biencoder that only outputs the context embedding at eval time
    """

    @classmethod
    def history_class(cls):
        return GoalOrientedHistory

    def build_dictionary(self):
        """
        Return the constructed dictionary, which will be set to self.dict.

        If you need to add additional tokens to the dictionary, this is likely
        the right place to do it.
        """
        # Tokens shouldn't be added
        d = self.dictionary_class()(self.opt)
        return d

    def build_history(self):
        """Return the constructed history object."""
        return self.history_class()(
            self.opt,
            self.text_truncate,
            self.histsz,
            "_partner_say",
            "_self_say",
            self.dict,
            MISSING_SAY_TAG,
        )

    def match_batch(self, batch_reply, valid_inds, output=None):
        batch_reply = super().match_batch(batch_reply, valid_inds, output)
        if output.embedding_ctx is not None:
            for i, ectx in zip(valid_inds, output.embedding_ctx):
                batch_reply[i].force_set("embedding_ctx", ectx)
        return batch_reply

    def eval_step(self, batch):
        """Just return the context embedding here"""
        with torch.no_grad():
            if hasattr(self.model, "module"):
                weights, context_h = self.model.module.encode_context_memory(
                    batch.text_vec, None, context_segments=None
                )
            else:
                weights, context_h = self.model.encode_context_memory(
                    batch.text_vec, None, context_segments=None
                )
            return Output(embedding_ctx=context_h)


class TopKRLAgent(LightBiencoderAgent):
    """TopkRL model is a biencoder that outputs the context embedding
    concatenated with the topk candidate embeddings in a (k+1, emb-size) tensor
    at eval time
    """

    @classmethod
    def history_class(cls):
        return GoalOrientedHistory

    def build_dictionary(self):
        """
        Return the constructed dictionary, which will be set to self.dict.

        If you need to add additional tokens to the dictionary, this is likely
        the right place to do it.
        """
        # Tokens shouldn't be added
        d = self.dictionary_class()(self.opt)
        return d

    def build_history(self):
        """Return the constructed history object."""
        return self.history_class()(
            self.opt,
            self.text_truncate,
            self.histsz,
            "_partner_say",
            "_self_say",
            self.dict,
            MISSING_SAY_TAG,
        )

    def match_batch(self, batch_reply, valid_inds, output=None):
        batch_reply = super().match_batch(batch_reply, valid_inds, output)

        if output.embedding_ctx is not None:
            for i, ectx, cands, cand_hs in zip(
                valid_inds, output.embedding_ctx, output.cands, output.cand_hs
            ):
                batch_reply[i].force_set("embedding_ctx", ectx)
                batch_reply[i].force_set("cand_hs", cand_hs)
                batch_reply[i].force_set("cands", cands)
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

    def train_step(self, batch):
        """Evaluate a single batch of examples."""
        if batch.text_vec is None and batch.image is None:
            return
        batchsize = (
            batch.text_vec.size(0)
            if batch.text_vec is not None
            else batch.image.size(0)
        )
        # self.model.eval()

        cands, cand_vecs, label_inds = self._build_candidates(
            batch, source=self.eval_candidates, mode="train"
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
        # print("RANK TOP K", self.rank_top_k)
        if self.rank_top_k > 0:
            _, ranks = scores.topk(
                min(self.rank_top_k, scores.size(1)), 1, largest=True
            )
        else:
            _, ranks = scores.sort(1, descending=True)
        ranks = ranks.cpu()
        # print("RANKS SIZE", ranks.size())
        max_preds = max(self.opt["cap_num_predictions"], self.opt["rank_top_k"])
        cand_preds = []
        cand_hs = []
        for i, ordering in enumerate(ranks):
            if cand_vecs.dim() == 2:
                cand_list = cands
                cand_encs_list = cand_encs
            elif cand_vecs.dim() == 3:
                cand_list = cands[i]
                cand_encs_list = cand_encs[i]
            # using a generator instead of a list comprehension allows
            # to cap the number of elements.
            cand_preds_generator = (
                cand_list[rank] for rank in ordering if rank < len(cand_list)
            )
            cand_encs_generator = (
                cand_encs_list[rank] for rank in ordering if rank < len(cand_encs_list)
            )
            cand_preds.append(list(islice(cand_preds_generator, max_preds)))
            cand_hs.append(list(islice(cand_encs_generator, max_preds)))
        return Output(embedding_ctx=context_h, cands=cand_preds, cand_hs=cand_hs)

    def eval_step(self, batch):
        """Evaluate a single batch of examples."""
        if batch.text_vec is None and batch.image is None:
            return
        batchsize = (
            batch.text_vec.size(0)
            if batch.text_vec is not None
            else batch.image.size(0)
        )
        self.model.eval()

        cands, cand_vecs, label_inds = self._build_candidates(
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
        # print("RANK TOP K", self.rank_top_k)
        if self.rank_top_k > 0:
            _, ranks = scores.topk(
                min(self.rank_top_k, scores.size(1)), 1, largest=True
            )
        else:
            _, ranks = scores.sort(1, descending=True)
        ranks = ranks.cpu()
        # print("RANKS SIZE", ranks.size())
        max_preds = max(self.opt["cap_num_predictions"], self.opt["rank_top_k"])
        cand_preds = []
        cand_hs = []
        for i, ordering in enumerate(ranks):
            if cand_vecs.dim() == 2:
                cand_list = cands
                cand_encs_list = cand_encs
            elif cand_vecs.dim() == 3:
                cand_list = cands[i]
                cand_encs_list = cand_encs[i]
            # using a generator instead of a list comprehension allows
            # to cap the number of elements.
            cand_preds_generator = (
                cand_list[rank] for rank in ordering if rank < len(cand_list)
            )
            cand_encs_generator = (
                cand_encs_list[rank] for rank in ordering if rank < len(cand_encs_list)
            )
            cand_preds.append(list(islice(cand_preds_generator, max_preds)))
            cand_hs.append(list(islice(cand_encs_generator, max_preds)))
        return Output(embedding_ctx=context_h, cands=cand_preds, cand_hs=cand_hs)

    # def observe(self, observation, self_observe=True):
    #     """
    #     Process incoming message in preparation for producing a response.
    #     This includes remembering the past history of the conversation.
    #     """
    #     return super().observe(observation)
    #     # observation = Message(observation)
    #     # if self_observe:
    #     #     reply = self.last_reply(use_reply=self.opt.get('use_reply', 'label'))
    #     #     self.history.update_history(observation, add_next=reply)
    #     # else:
    #     #     self.history.update_history(observation, add_next=None)
    #     # self.observation = observation
    #     # return self.vectorize(
    #     #     self.observation,
    #     #     self.history,
    #     #     text_truncate=self.text_truncate,
    #     #     label_truncate=self.label_truncate,
    #     # )


class VerbAnalysisAgent(LightBiencoderAgent):
    """TopkRL model is a biencoder that outputs the context embedding
    concatenated with the topk candidate embeddings in a (k+1, emb-size) tensor
    at eval time
    """

    @classmethod
    def history_class(cls):
        return GoalOrientedHistory

    def build_dictionary(self):
        """
        Return the constructed dictionary, which will be set to self.dict.

        If you need to add additional tokens to the dictionary, this is likely
        the right place to do it.
        """
        # Tokens shouldn't be added
        d = self.dictionary_class()(self.opt)
        return d

    def build_history(self):
        """Return the constructed history object."""
        return self.history_class()(
            self.opt,
            self.text_truncate,
            self.histsz,
            "_partner_say",
            "_self_say",
            self.dict,
            MISSING_SAY_TAG,
        )

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
                batch_reply[i].force_set("embedding_ctx", ectx)
                batch_reply[i].force_set("cand_hs", cand_hs)
                batch_reply[i].force_set("cands", cands)
                batch_reply[i].force_set("scores", scores)
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
        print("HI")
        if batch.text_vec is None and batch.image is None:
            return
        batchsize = (
            batch.text_vec.size(0)
            if batch.text_vec is not None
            else batch.image.size(0)
        )
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

        return Output(
            embedding_ctx=context_h, scores=scores, cands=[cands], cand_hs=cand_encs
        )

    def observe(self, observation, self_observe=True):
        """
        Process incoming message in preparation for producing a response.
        This includes remembering the past history of the conversation.
        """
        return super().observe(observation)
        # observation = Message(observation)
        # reply = self.last_reply(use_reply=self.opt.get('use_reply', 'label'))
        # if self_observe:
        #     self.history.update_history(observation, add_next=reply)
        # else:
        #     self.history.update_history(observation, add_next=None)
        # self.observation = observation
        # return self.vectorize(
        #     self.observation,
        #     self.history,
        #     text_truncate=self.text_truncate,
        #     label_truncate=self.label_truncate,
        # )


class NewClusterEncoderAgent(LightBiencoderAgent):
    @classmethod
    def history_class(cls):
        return GoalOrientedHistory

    def build_dictionary(self):
        """
        Return the constructed dictionary, which will be set to self.dict.

        If you need to add additional tokens to the dictionary, this is likely
        the right place to do it.
        """
        d = self.dictionary_class()(self.opt)
        return d

    def build_history(self):
        """Return the constructed history object."""
        return self.history_class()(
            self.opt,
            self.text_truncate,
            self.histsz,
            "_partner_say",
            "_self_say",
            self.dict,
            MISSING_SAY_TAG,
        )

    def match_batch(self, batch_reply, valid_inds, output=None):
        batch_reply = super().match_batch(batch_reply, valid_inds, output)

        if output.embedding_ctx is not None:
            for i, ectx in zip(valid_inds, output.embedding_ctx):
                batch_reply[i].force_set("embedding_ctx", ectx)

        return batch_reply

    def eval_step(self, batch):
        """Evaluate a single batch of examples."""
        if batch.text_vec is None:
            return
        self.model.eval()

        token_idx_ctxt, segment_idx_ctxt, mask_ctxt = to_bert_input(
            batch.text_vec, self.NULL_IDX
        )
        embedding_ctxt, _ = self.model(
            token_idx_ctxt, segment_idx_ctxt, mask_ctxt, None, None, None
        )
        return Output(embedding_ctx=embedding_ctxt)

    def observe(self, observation, self_observe=True):
        """
        Process incoming message in preparation for producing a response.
        This includes remembering the past history of the conversation.
        """
        return super().observe(observation)
        # observation = Message(observation)
        # reply = self.last_reply(use_reply=self.opt.get('use_reply', 'label'))
        # if self_observe:
        #     self.history.update_history(observation, add_next=reply)
        # else:
        #     self.history.update_history(observation, add_next=None)
        # self.observation = observation
        # return self.vectorize(
        #     self.observation,
        #     self.history,
        #     text_truncate=self.text_truncate,
        #     label_truncate=self.label_truncate,
        # )


class ClusterEncoderAgent(BiEncoderRankerAgent):
    """Cluster encoder model is used only to create clusters, not in the main
    training loops or envs
    """

    @classmethod
    def history_class(cls):
        return GoalOrientedHistory

    # def build_dictionary(self):
    #     """
    #     Return the constructed dictionary, which will be set to self.dict.
    #
    #     If you need to add additional tokens to the dictionary, this is likely
    #     the right place to do it.
    #     """
    #     d = self.dictionary_class()(self.opt)
    #     # if self.opt.get('person_tokens'):
    #     #     d[self.P1_TOKEN] = 999_999_999
    #     #     d[self.P2_TOKEN] = 999_999_998
    #     return d

    def build_history(self):
        """Return the constructed history object."""
        return self.history_class()(
            self.opt,
            self.text_truncate,
            self.histsz,
            "_partner_say",
            "_self_say",
            self.dict,
            MISSING_SAY_TAG,
        )

    def match_batch(self, batch_reply, valid_inds, output=None):
        batch_reply = super().match_batch(batch_reply, valid_inds, output)

        if output.embedding_ctx is not None:
            for i, ectx in zip(valid_inds, output.embedding_ctx):
                batch_reply[i].force_set("embedding_ctx", ectx)

        return batch_reply

    def eval_step(self, batch):
        """Evaluate a single batch of examples."""
        if batch.text_vec is None:
            return
        self.model.eval()

        token_idx_ctxt, segment_idx_ctxt, mask_ctxt = to_bert_input(
            batch.text_vec, self.NULL_IDX
        )
        embedding_ctxt, _ = self.model(
            token_idx_ctxt, segment_idx_ctxt, mask_ctxt, None, None, None
        )
        return Output(embedding_ctx=embedding_ctxt)

    def observe(self, observation, self_observe=True):
        """
        Process incoming message in preparation for producing a response.
        This includes remembering the past history of the conversation.
        """
        return super().observe(observation)
        # observation = Message(observation)
        # reply = self.last_reply(use_reply=self.opt.get('use_reply', 'label'))
        # if self_observe:
        #     self.history.update_history(observation, add_next=reply)
        # else:
        #     self.history.update_history(observation, add_next=None)
        # self.observation = observation
        # return self.vectorize(
        #     self.observation,
        #     self.history,
        #     text_truncate=self.text_truncate,
        #     label_truncate=self.label_truncate,
        # )
