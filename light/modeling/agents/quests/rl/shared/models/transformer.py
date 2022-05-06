#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
LIGHT Transformer Agents.
"""
from typing import Optional
from parlai.core.params import ParlaiParser
from parlai.core.opt import Opt
from parlai.agents.transformer.polyencoder import PolyencoderAgent
from parlai.agents.transformer.biencoder import BiencoderAgent
from parlai.core.torch_agent import Output, Batch
from parlai.utils.torch import padded_3d
from parlai.utils.misc import warn_once
from parlai.core.message import Message
from parlai.utils.strings import normalize_reply

from itertools import islice
import torch
import json
import random
import os


class LightBiencoderAgent(BiencoderAgent):
    def __init__(self, opt: Opt, shared=None):
        super().__init__(opt, shared)

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

        return scores

    def _set_label_cands_vec(self, obs, add_start, add_end, truncate):
        """
        Set the 'label_candidates_vec' field in the observation.
        Useful to override to change vectorization behavior.
        """
        if "labels" in obs:
            cands_key = "candidates"
        else:
            cands_key = "eval_candidates"
        if self.opt[cands_key] not in ["inline", "batch-all-cands"]:
            # vectorize label candidates if and only if we are using inline
            # candidates
            if "label_candidates" not in obs:
                return obs

        if "label_candidates_vecs" in obs:
            if truncate is not None:
                # check truncation of pre-computed vectors
                vecs = obs["label_candidates_vecs"]
                for i, c in enumerate(vecs):
                    vecs[i] = self._check_truncate(c, truncate)
        elif self.rank_candidates and obs.get("label_candidates"):
            obs.force_set("label_candidates", list(obs["label_candidates"]))
            obs["label_candidates_vecs"] = [
                self._vectorize_text(c, add_start, add_end, truncate, False)
                for c in obs["label_candidates"]
            ]
        return obs

    def _build_candidates(self, batch, source, mode):
        """
        Build a candidate set for this batch.
        :param batch:
            a Batch object (defined in torch_agent.py)
        :param source:
            the source from which candidates should be built, one of
            ['batch', 'batch-all-cands', 'inline', 'fixed']
        :param mode:
            'train' or 'eval'
        :return: tuple of tensors (label_inds, cands, cand_vecs)
            label_inds: A [bsz] LongTensor of the indices of the labels for each
                example from its respective candidate set
            cands: A [num_cands] list of (text) candidates
                OR a [batchsize] list of such lists if source=='inline'
            cand_vecs: A padded [num_cands, seqlen] LongTensor of vectorized candidates
                OR a [batchsize, num_cands, seqlen] LongTensor if source=='inline'
        Possible sources of candidates:
            * batch: the set of all labels in this batch
                Use all labels in the batch as the candidate set (with all but the
                example's label being treated as negatives).
                Note: with this setting, the candidate set is identical for all
                examples in a batch. This option may be undesirable if it is possible
                for duplicate labels to occur in a batch, since the second instance of
                the correct label will be treated as a negative.
            * batch-all-cands: the set of all candidates in this batch
                Use all candidates in the batch as candidate set.
                Note 1: This can result in a very large number of candidates.
                Note 2: In this case we will deduplicate candidates.
                Note 3: just like with 'batch' the candidate set is identical
                for all examples in a batch.
            * inline: batch_size lists, one list per example
                If each example comes with a list of possible candidates, use those.
                Note: With this setting, each example will have its own candidate set.
            * fixed: one global candidate list, provided in a file from the user
                If self.fixed_candidates is not None, use a set of fixed candidates for
                all examples.
                Note: this setting is not recommended for training unless the
                universe of possible candidates is very small.
            * vocab: one global candidate list, extracted from the vocabulary with the
                exception of self.NULL_IDX.
        """
        label_vecs = batch.label_vec  # [bsz] list of lists of LongTensors
        label_inds = None
        batchsize = (
            batch.text_vec.size(0)
            if batch.text_vec is not None
            else batch.image.size(0)
        )
        if label_vecs is not None:
            assert label_vecs.dim() == 2
        print(source)
        source = "fixed"
        print(self.fixed_candidates)
        if source == "batch":
            warn_once(
                "[ Executing {} mode with batch labels as set of candidates. ]"
                "".format(mode)
            )
            if batchsize == 1:
                warn_once(
                    "[ Warning: using candidate source 'batch' and observed a "
                    "batch of size 1. This may be due to uneven batch sizes at "
                    "the end of an epoch. ]"
                )
            if label_vecs is None:
                raise ValueError(
                    "If using candidate source 'batch', then batch.label_vec cannot be "
                    "None."
                )
            cands = batch.labels
            cand_vecs = label_vecs
            label_inds = label_vecs.new_tensor(range(batchsize))

        elif source == "batch-all-cands":
            warn_once(
                "[ Executing {} mode with all candidates provided in the batch ]"
                "".format(mode)
            )
            if batch.candidate_vecs is None:
                raise ValueError(
                    "If using candidate source 'batch-all-cands', then batch."
                    "candidate_vecs cannot be None. If your task does not have "
                    "inline candidates, consider using one of "
                    "--{m}={{'batch','fixed','vocab'}}."
                    "".format(m="candidates" if mode == "train" else "eval-candidates")
                )
            # initialize the list of cands with the labels
            cands = []
            all_cands_vecs = []
            # dictionary used for deduplication
            cands_to_id = {}
            for i, cands_for_sample in enumerate(batch.candidates):
                for j, cand in enumerate(cands_for_sample):
                    if cand not in cands_to_id:
                        cands.append(cand)
                        cands_to_id[cand] = len(cands_to_id)
                        all_cands_vecs.append(batch.candidate_vecs[i][j])
            cand_vecs, _ = self._pad_tensor(all_cands_vecs)
            label_inds = label_vecs.new_tensor(
                [cands_to_id[label] for label in batch.labels]
            )

        elif source == "fixed":
            if self.fixed_candidates is None:
                raise ValueError(
                    "If using candidate source 'fixed', then you must provide the path "
                    "to a file of candidates with the flag --fixed-candidates-path or "
                    "the name of a task with --fixed-candidates-task."
                )
            warn_once(
                "[ Executing {} mode with a common set of fixed candidates "
                "(n = {}). ]".format(mode, len(self.fixed_candidates))
            )

            if batch.candidate_vecs is None:
                cands = self.fixed_candidates
                cand_vecs = self.fixed_candidate_vecs

                if label_vecs is not None:
                    label_inds = label_vecs.new_empty((batchsize))
                    bad_batch = False
                    for batch_idx, label_vec in enumerate(label_vecs):
                        max_c_len = cand_vecs.size(1)
                        label_vec_pad = label_vec.new_zeros(max_c_len).fill_(
                            self.NULL_IDX
                        )
                        if max_c_len < len(label_vec):
                            label_vec = label_vec[0:max_c_len]
                        label_vec_pad[0 : label_vec.size(0)] = label_vec
                        label_inds[batch_idx] = self._find_match(
                            cand_vecs, label_vec_pad
                        )
                        if label_inds[batch_idx] == -1:
                            bad_batch = True
                    if bad_batch:
                        if self.ignore_bad_candidates and not self.is_training:
                            label_inds = None
                        else:
                            raise RuntimeError(
                                "At least one of your examples has a set of label candidates "
                                "that does not contain the label. To ignore this error "
                                "set `--ignore-bad-candidates True`."
                            )
            else:
                warn_once(
                    "[ Executing {} mode with provided inline set of candidates ]"
                    "".format(mode)
                )
                cands = batch.candidates
                cand_vecs = padded_3d(
                    batch.candidate_vecs,
                    self.NULL_IDX,
                    use_cuda=self.use_cuda,
                    fp16friendly=self.fp16,
                )
                if label_vecs is not None:
                    label_inds = label_vecs.new_empty((batchsize))
                    bad_batch = False
                    for i, label_vec in enumerate(label_vecs):
                        label_vec_pad = label_vec.new_zeros(cand_vecs[i].size(1)).fill_(
                            self.NULL_IDX
                        )
                        if cand_vecs[i].size(1) < len(label_vec):
                            label_vec = label_vec[0 : cand_vecs[i].size(1)]
                        label_vec_pad[0 : label_vec.size(0)] = label_vec
                        label_inds[i] = self._find_match(cand_vecs[i], label_vec_pad)
                        if label_inds[i] == -1:
                            bad_batch = True
                    if bad_batch:
                        if self.ignore_bad_candidates and not self.is_training:
                            label_inds = None
                        else:
                            raise RuntimeError(
                                "At least one of your examples has a set of label candidates "
                                "that does not contain the label. To ignore this error "
                                "set `--ignore-bad-candidates True`."
                            )

        elif source == "inline":
            warn_once(
                "[ Executing {} mode with provided inline set of candidates ]"
                "".format(mode)
            )
            if batch.candidate_vecs is None:
                raise ValueError(
                    "If using candidate source 'inline', then batch.candidate_vecs "
                    "cannot be None. If your task does not have inline candidates, "
                    "consider using one of --{m}={{'batch','fixed','vocab'}}."
                    "".format(m="candidates" if mode == "train" else "eval-candidates")
                )
            cands = batch.candidates
            cand_vecs = padded_3d(
                batch.candidate_vecs,
                self.NULL_IDX,
                use_cuda=self.use_cuda,
                fp16friendly=self.fp16,
            )
            if label_vecs is not None:
                label_inds = label_vecs.new_empty((batchsize))
                bad_batch = False
                for i, label_vec in enumerate(label_vecs):
                    label_vec_pad = label_vec.new_zeros(cand_vecs[i].size(1)).fill_(
                        self.NULL_IDX
                    )
                    if cand_vecs[i].size(1) < len(label_vec):
                        label_vec = label_vec[0 : cand_vecs[i].size(1)]
                    label_vec_pad[0 : label_vec.size(0)] = label_vec
                    label_inds[i] = self._find_match(cand_vecs[i], label_vec_pad)
                    if label_inds[i] == -1:
                        bad_batch = True
                if bad_batch:
                    if self.ignore_bad_candidates and not self.is_training:
                        label_inds = None
                    else:
                        raise RuntimeError(
                            "At least one of your examples has a set of label candidates "
                            "that does not contain the label. To ignore this error "
                            "set `--ignore-bad-candidates True`."
                        )
        elif source == "vocab":
            warn_once(
                "[ Executing {} mode with tokens from vocabulary as candidates. ]"
                "".format(mode)
            )
            cands = self.vocab_candidates
            cand_vecs = self.vocab_candidate_vecs
            # NOTE: label_inds is None here, as we will not find the label in
            # the set of vocab candidates
        else:
            raise Exception("Unrecognized source: %s" % source)

        return (cands, cand_vecs, label_inds)

    # def _make_candidate_encs(self, vecs, path):
    #     """
    #     Encode candidates from candidate vectors.
    #
    #     Requires encode_candidates() to be implemented.
    #     """
    #     cand_encs = []
    #     bsz = self.opt.get('encode_candidate_vecs_batchsize', 256)
    #     vec_batches = [vecs[i : i + bsz] for i in range(0, len(vecs), bsz)]
    #     print(
    #         "[ Encoding fixed candidates set from ({} batch(es) of up to {}) ]"
    #         "".format(len(vec_batches), bsz)
    #     )
    #     self.model.eval()
    #     with torch.no_grad():
    #         for vec_batch in tqdm(vec_batches):
    #             cand_encs.append(self.encode_candidates(vec_batch))
    #     return torch.cat(cand_encs, 0)

    def set_fixed_candidates(self, shared):
        """
        Load a set of fixed candidates and their vectors (or vectorize them here).
        self.fixed_candidates will contain a [num_cands] list of strings
        self.fixed_candidate_vecs will contain a [num_cands, seq_len] LongTensor
        See the note on the --fixed-candidate-vecs flag for an explanation of the
        'reuse', 'replace', or path options.
        Note: TorchRankerAgent by default converts candidates to vectors by vectorizing
        in the common sense (i.e., replacing each token with its index in the
        dictionary). If a child model wants to additionally perform encoding, it can
        overwrite the vectorize_fixed_candidates() method to produce encoded vectors
        instead of just vectorized ones.
        """
        if shared:
            self.fixed_candidates = shared["fixed_candidates"]
            self.fixed_candidate_vecs = shared["fixed_candidate_vecs"]
            self.fixed_candidate_encs = shared["fixed_candidate_encs"]
            self.num_fixed_candidates = shared["num_fixed_candidates"]

        else:
            self.num_fixed_candidates = 0
            opt = self.opt
            cand_path = self.fixed_candidates_path
            if "fixed" in (self.candidates, self.eval_candidates) and cand_path:
                # Load candidates
                print("[ Loading fixed candidate set from {} ]".format(cand_path))
                with open(cand_path, "r", encoding="utf-8") as f:
                    cands = [line.strip() for line in f.readlines()]
                # Load or create candidate vectors
                if os.path.isfile(self.opt["fixed_candidate_vecs"]):
                    vecs_path = opt["fixed_candidate_vecs"]
                    vecs = self.load_candidates(vecs_path)
                else:
                    setting = self.opt["fixed_candidate_vecs"]
                    model_dir, model_file = os.path.split(self.opt["model_file"])
                    model_name = os.path.splitext(model_file)[0]
                    cands_name = os.path.splitext(os.path.basename(cand_path))[0]
                    vecs_path = os.path.join(
                        model_dir, ".".join([model_name, cands_name, "vecs"])
                    )
                    if setting == "reuse" and os.path.isfile(vecs_path):
                        vecs = self.load_candidates(vecs_path)
                    else:  # setting == 'replace' OR generating for the first time
                        vecs = self._make_candidate_vecs(cands)
                        self._save_candidates(vecs, vecs_path)
                self.fixed_candidates = cands
                self.fixed_candidate_vecs = vecs
                if self.use_cuda:
                    self.fixed_candidate_vecs = self.fixed_candidate_vecs.cuda()
                if self.encode_candidate_vecs:
                    # candidate encodings are fixed so set them up now
                    enc_path = os.path.join(
                        model_dir, ".".join([model_name, cands_name, "encs"])
                    )
                    if setting == "reuse" and os.path.isfile(enc_path):
                        encs = self.load_candidates(enc_path, cand_type="encodings")
                    else:
                        encs = self._make_candidate_encs(self.fixed_candidate_vecs)
                        # encs = self._make_candidate_encs(
                        #     self.fixed_candidate_vecs, path=enc_path
                        # )
                        self._save_candidates(
                            encs, path=enc_path, cand_type="encodings"
                        )
                    self.fixed_candidate_encs = encs
                    if self.use_cuda:
                        self.fixed_candidate_encs = self.fixed_candidate_encs.cuda()
                    if self.fp16:
                        self.fixed_candidate_encs = self.fixed_candidate_encs.half()
                    else:
                        self.fixed_candidate_encs = self.fixed_candidate_encs.float()
                else:
                    self.fixed_candidate_encs = None
            else:
                self.fixed_candidates = None
                self.fixed_candidate_vecs = None
                self.fixed_candidate_encs = None

    def eval_step(self, batch):
        """
        Evaluate a single batch of examples.
        """
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
        if self.encode_candidate_vecs and self.eval_candidates in ["fixed", "vocab"]:
            # if we cached candidate encodings for a fixed list of candidates,
            # pass those into the score_candidates function
            if self.fixed_candidate_encs is None:
                self.fixed_candidate_encs = self._make_candidate_encs(
                    cand_vecs
                ).detach()
            if self.eval_candidates == "fixed":
                cand_encs = self.fixed_candidate_encs
            elif self.eval_candidates == "vocab":
                cand_encs = self.vocab_candidate_encs

        scores = self.score_candidates(batch, cand_vecs, cand_encs=cand_encs)
        if self.rank_top_k > 0:
            sorted_scores, ranks = scores.topk(
                min(self.rank_top_k, scores.size(1)), 1, largest=True
            )
        else:
            sorted_scores, ranks = scores.sort(1, descending=True)

        if self.opt.get("return_cand_scores", False):
            sorted_scores = sorted_scores.cpu()
        else:
            sorted_scores = None

        # Update metrics
        if label_inds is not None:
            loss = self.criterion(scores, label_inds)
            self.record_local_metric("loss", AverageMetric.many(loss))
            ranks_m = []
            mrrs_m = []
            for b in range(batchsize):
                rank = (ranks[b] == label_inds[b]).nonzero()
                rank = rank.item() if len(rank) == 1 else scores.size(1)
                ranks_m.append(1 + rank)
                mrrs_m.append(1.0 / (1 + rank))
            self.record_local_metric("rank", AverageMetric.many(ranks_m))
            self.record_local_metric("mrr", AverageMetric.many(mrrs_m))

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

        if self.opt.get("inference", "max") == "max":
            preds = [cand_preds[i][0] for i in range(batchsize)]
        else:
            # Top-k inference.
            preds = []
            for i in range(batchsize):
                preds.append(random.choice(cand_preds[i][0 : self.opt["topk"]]))

        return Output(preds, cand_preds, sorted_scores=sorted_scores)


class LightPolyencoderAgent(PolyencoderAgent):
    @classmethod
    def add_cmdline_args(
        cls, parser: ParlaiParser, partial_opt: Optional[Opt] = None
    ) -> ParlaiParser:
        super().add_cmdline_args(parser, partial_opt=partial_opt)
        agent = parser.add_argument_group("LIGHT poly agent")
        agent.add_argument(
            "--from-speaker-bonus",
            type=float,
            default=20,
            help="We boost utterances from the same speaker",
        )
        agent.add_argument(
            "--to-speaker-bonus",
            type=float,
            default=20,
            help="We boost utterances to the same speaker",
        )
        agent.add_argument(
            "--boring-alpha",
            type=float,
            default=-50,
            help="We boost utterances to the same speaker",
        )
        agent.add_argument(
            "--retrieve-segments",
            type="bool",
            default=False,
            help="Segment retrieval system",
        )
        agent.add_argument(
            "--block-ngrams",
            type=int,
            default=0,
            help="Segment retrieval system",
        )
        return parser

    def __init__(self, opt, shared=None):
        super().__init__(opt, shared)
        # load agent speak stop list.
        fnames = [
            opt.get(
                "partner_trainset",
                "/checkpoint/jase/projects/light/dialog/agent_to_utterance_partner_trainset.txt",
            ),
            opt.get(
                "trainset",
                "/checkpoint/jase/projects/light/dialog/agent_to_utterance_trainset.txt",
            ),
            opt.get(
                "baseforms",
                "/checkpoint/jase/projects/light/beatthehobbot/cands/baseforms.json",
            ),
        ]
        self._debug = False
        self.actingscore = False
        self.boring_alpha = self.opt["boring_alpha"]
        if shared is not None and "block_utt_given_self" in shared:
            self._block_utt_given_self = shared["block_utt_given_self"]
            self._block_utt_given_partner = shared["block_utt_given_partner"]
            self._block_utt_baseforms = shared["block_utt_baseforms"]
            self.boring = shared["boring"]
        else:
            self.compute_boring_scores()
            self._block_utt_given_self = {}
            self._block_utt_given_partner = {}
            self._block_utt_baseforms = {}
            for fname in fnames:
                if fname.endswith(".json"):
                    with open(fname) as json_file:
                        data = json.load(json_file)
                    for d in data:
                        self._block_utt_baseforms[d[0]] = d[1]
                else:
                    file = open(fname, "r")
                    data = file.readlines()
                    for d in data:
                        i1 = d.find(":")
                        name = d[1:i1]
                        utt = d[i1 + 1 : -1]
                        if "partner" in fname:
                            utts = self.split_into_segments(utt)
                            for utt in utts:
                                if utt not in self._block_utt_given_self:
                                    self._block_utt_given_self[utt] = []
                                self._block_utt_given_self[utt].append(name)
                        else:
                            utts = self.split_into_segments(utt)
                            for utt in utts:
                                if utt not in self._block_utt_given_partner:
                                    self._block_utt_given_partner[utt] = []
                                self._block_utt_given_partner[utt].append(name)

    def split_into_segments(self, txt):
        if not self.opt.get("retrieve_segments", False):
            return [txt]
        s = []
        n = ""
        splits = ",.?!"
        for ind, t in enumerate(txt):
            n += t
            if t == " " and len(n) > 4 and ind > 0 and txt[ind - 1] in splits:
                s.append(n.rstrip(" "))
                n = ""
        if len(n) > 0:
            s.append(n.rstrip(" "))
        return s

    def share(self):
        s = super().share()
        s["block_utt_given_self"] = self._block_utt_given_self
        s["block_utt_given_partner"] = self._block_utt_given_partner
        s["block_utt_baseforms"] = self._block_utt_baseforms
        s["boring"] = self.boring
        return s

    def observe(self, observation):
        """
        Process incoming message in preparation for producing a response.
        This includes remembering the past history of the conversation.
        """
        # TODO: Migration plan: TorchAgent currently supports being passed
        # observations as vanilla dicts for legacy interop; eventually we
        # want to remove this behavior and demand that teachers return Messages
        observation = Message(observation)

        # Sanity check everything is in order
        self._validate_observe_invariants()

        if observation.get("episode_done"):
            self.__expecting_clear_history = True
        elif "labels" in observation or "eval_labels" in observation:
            # make sure we note that we're expecting a reply in the future
            self.__expecting_to_reply = True

        self.observation = observation
        # Update the history using the observation.
        # We may also consider adding a temporary string to the history
        # using the `get_temp_history()` function: this string will
        # persist until it is updated.
        self.history.update_history(
            observation, temp_history=self.get_temp_history(observation)
        )
        return self.vectorize(
            observation,
            self.history,
            text_truncate=self.text_truncate,
            label_truncate=self.label_truncate,
        )

    def eval_step(self, batch):
        """
        Evaluate a single batch of examples.
        """
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
        if self.encode_candidate_vecs and self.eval_candidates in ["fixed", "vocab"]:
            # if we cached candidate encodings for a fixed list of candidates,
            # pass those into the score_candidates function
            if self.fixed_candidate_encs is None:
                self.fixed_candidate_encs = self._make_candidate_encs(
                    cand_vecs
                ).detach()
            if self.eval_candidates == "fixed":
                cand_encs = self.fixed_candidate_encs
            elif self.eval_candidates == "vocab":
                cand_encs = self.vocab_candidate_encs

        if self.opt.get("retrieve_segments", False):
            best_cand = self.score_candidates_segments(
                batch, cands, cand_vecs, cand_encs=cand_encs
            )
            return Output([best_cand], [best_cand])
        else:
            scores = self.score_candidates(batch, cand_vecs, cand_encs=cand_encs)
            if self.rank_top_k > 0:
                sorted_scores, ranks = scores.topk(
                    min(self.rank_top_k, scores.size(1)), 1, largest=True
                )
            else:
                sorted_scores, ranks = scores.sort(1, descending=True)

        if self.opt.get("return_cand_scores", False):
            sorted_scores = sorted_scores.cpu()
        else:
            sorted_scores = None

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
            cand_preds = self.block_repeats(cand_preds)

        if self.opt.get("inference", "max") == "max":
            preds = [
                normalize_reply(cand_preds[i][0], version=2) for i in range(batchsize)
            ]
        else:
            # Top-k inference.
            preds = []
            for i in range(batchsize):
                preds.append(random.choice(cand_preds[i][0 : self.opt["topk"]]))

        return Output(preds, cand_preds, sorted_scores=sorted_scores)

    def score_candidates_segments(
        self, batch, cands, cand_vecs, cand_encs=None, scores_only=False
    ):
        """
        Scores segments, turn by turn.
        """
        # print(self.history.get_history_str())
        bsz = self._get_batch_size(batch)

        # LOOP 1
        full_text = batch["observations"][0]["full_text"]
        batch["observations"][0].force_set("full_text", full_text + "\n_SOS_ ")
        vec = self._vectorize_text(
            batch["observations"][0]["full_text"],
            truncate=self.text_truncate,
            truncate_left=False,
            add_start=True,
            add_end=True,
        )
        batch["text_vec"] = vec.unsqueeze(0)
        ctxt_rep, ctxt_rep_mask, _ = self.model(**self._model_context_input(batch))
        cand_rep = cand_encs
        scores = self.model(
            ctxt_rep=ctxt_rep, ctxt_rep_mask=ctxt_rep_mask, cand_rep=cand_rep
        )
        # Can't do EOS on loop1:
        if not hasattr(self, "EOS"):
            for i, c in enumerate(cands):
                if c == "_EOS_":
                    self.EOS = i
        scores[0][self.EOS] = -10000
        sorted_scores, ranks = scores.topk(min(100, scores.size(1)), 1, largest=True)
        cand_preds = []
        for i in range(len(ranks[0])):
            cand_preds.append(cands[int(ranks[0][i])])
        cand_preds = self.block_repeats([cand_preds])
        best_cand = cand_preds[0][0]

        # LOOP 2
        batch["observations"][0].force_set(
            "full_text", full_text + "\n_SOS_ " + best_cand
        )
        vec = self._vectorize_text(
            batch["observations"][0]["full_text"],
            truncate=self.text_truncate,
            truncate_left=False,
            add_start=True,
            add_end=True,
        )
        batch["text_vec"] = vec.unsqueeze(0)
        ctxt_rep, ctxt_rep_mask, _ = self.model(**self._model_context_input(batch))
        cand_rep = cand_encs
        scores = self.model(
            ctxt_rep=ctxt_rep, ctxt_rep_mask=ctxt_rep_mask, cand_rep=cand_rep
        )
        sorted_scores, ranks = scores.topk(min(100, scores.size(1)), 1, largest=True)
        cand_preds = []
        for i in range(len(ranks[0])):
            cand_preds.append(cands[int(ranks[0][i])])
        cand_preds = self.block_repeats([cand_preds], [[best_cand]])
        best_cand2 = cand_preds[0][0]

        final = best_cand + " " + best_cand2
        final = final.rstrip(",")
        final = final.replace("_EOS_", ".")
        final = normalize_reply(final, version=2)

        return final

    def score_candidates(self, batch, cand_vecs, cand_encs=None, scores_only=False):
        """
        This is an override from the polyencoder function in order to cache
        the context representation in the case of `self.actingscore`.
        """
        # print(self.history.get_history_str())
        bsz = self._get_batch_size(batch)

        ctxt_rep, ctxt_rep_mask, _ = self.model(**self._model_context_input(batch))

        # cache this for next time
        if self.actingscore:
            self.ctxt = (ctxt_rep, ctxt_rep_mask)

        if cand_encs is not None:
            if bsz == 1:
                cand_rep = cand_encs
            else:
                cand_rep = cand_encs.expand(bsz, cand_encs.size(1), -1)
        # bsz x num cands x seq len
        elif len(cand_vecs.shape) == 3:
            _, _, cand_rep = self.model(cand_tokens=cand_vecs)
        # bsz x seq len (if batch cands) or num_cands x seq len (if fixed cands)
        elif len(cand_vecs.shape) == 2:
            _, _, cand_rep = self.model(cand_tokens=cand_vecs.unsqueeze(1))
            num_cands = cand_rep.size(0)  # will be bsz if using batch cands
            cand_rep = cand_rep.expand(num_cands, bsz, -1).transpose(0, 1).contiguous()
        scores = self.model(
            ctxt_rep=ctxt_rep, ctxt_rep_mask=ctxt_rep_mask, cand_rep=cand_rep
        )

        if not self.actingscore and hasattr(self, "boring"):
            use_alpha = self.boring_alpha
            # use the boring score unless the last two dialog turn were very boring:
            hist = self.history.get_history_str().split("\n")
            if len(hist) > 10:
                last_utt_len = len(hist[-2]) + len(hist[-4])
                # print(str(last_utt_len) + " " + hist[-2] + " | " + hist[-4])
                if last_utt_len < 50:
                    use_alpha = 0
            if use_alpha != 0:
                scores = scores.add(self.boring, alpha=use_alpha)

        return scores

    def compute_boring_scores(self):
        if self.opt["boring_alpha"] == 0:
            return
        if not self.actingscore and not hasattr(self, "boring"):
            print("[computing boringness..]")
            import math

            ban_set = set(
                [
                    "Well, if you must know, I killed my uncle because he raped my wife",  # *
                    "yes it will be the good of you",  # *
                    "Well can",  # *
                    "I",  # *
                    "Don",  # *
                    "If you don" "I'd rather be in the forest so don" "i don",
                    "I don not know.",
                    "I was just in the",
                    "ill just that",
                    "I i uh i cant",
                    "I can here you, and if don't back off i'll deal with you",
                    "You" "No",
                ]
            )

            fs = list(self.dict.freq.values())
            max_freq = math.log(max(fs))
            min_freq = math.log((min(fs) + 1e-8))
            cands, cand_vecs, label_inds = self._build_candidates(
                batch=Batch(text_vec=torch.zeros(1)),
                source=self.eval_candidates,
                mode="eval",
            )
            vs = torch.zeros(1, len(cand_vecs))
            sz = len(self.dict.ind2tok)
            ind2freq = torch.zeros(sz)
            ignore = -1
            for i in range(sz):
                tok = self.dict.ind2tok[i]
                ind2freq[i] = self.dict.freq[tok]
                if tok == ".":
                    ignore = i
            for i in range(len(cand_vecs)):
                v = cand_vecs[i]
                score = 0
                cnt = 0
                for j in range(1, v.size(0)):
                    if v[j] < 2:
                        # if cands[i] in ban_set:
                        #    print(cands[i])
                        #    #import pdb; pdb.set_trace()
                        break
                    ind = v[j]
                    if ind != ignore:
                        sc = ind2freq[ind]
                        sc2 = (math.log(sc) - min_freq) / (max_freq - min_freq)
                        sc3 = 1.0 - sc2
                        # if sc3 < 0.25:  sc3 = 0.25   # could have this
                        score += sc3
                        cnt += 1
                if cnt > 0 and cands[i] not in ban_set:
                    vs[0][i] = score / math.pow(cnt, 1)
                else:
                    # print("blocked: " + cands[i])
                    vs[0][i] = 100000  # don't use
                    # print(self.dict.vec2txt(v[1:cnt+2]) + " -> " + str(vs[0][i]))
            print("[done!]")
            self.boring = vs
            # for i in range(0,100000):
            #    if vs[i] < 0.12:
            #        print(self.dict.parse(cand_vecs[i][1:10]))
            # import ipdb; ipdb.set_trace()

    def eval_step_scoresonly(self, batch):
        """
        Only save the scores for each of the given candidates in
        self.scores. Returns dummy output.
        This is typically only used by the acting score agent,
        so that we can pre-comute the score of the fixed candidates
        given the context, and the compute the score of the human's
        message using the cached context.
        """
        if batch.text_vec is None and batch.image is None:
            return
        self.model.eval()

        cands, cand_vecs, label_inds = self._build_candidates(
            batch, source=self.eval_candidates, mode="eval"
        )

        cand_encs = None
        if self.encode_candidate_vecs and self.eval_candidates in ["fixed", "vocab"]:
            # if we cached candidate encodings for a fixed list of candidates,
            # pass those into the score_candidates function
            if self.fixed_candidate_encs is None:
                self.fixed_candidate_encs = self._make_candidate_encs(
                    cand_vecs
                ).detach()
            if self.eval_candidates == "fixed":
                cand_encs = self.fixed_candidate_encs
            elif self.eval_candidates == "vocab":
                cand_encs = self.vocab_candidate_encs

        self.scores = self.score_candidates(
            batch, cand_vecs, cand_encs=cand_encs, scores_only=True
        )

        # return dummy output
        return Output()

    def score_one_candidate(self, label_text):
        """
        Score one label using previous cached context.
        This is typically only used by the acting score agent,
        so that we can pre-comute the score of the fixed candidates
        given the context, and the compute the score of the human's
        message using the cached context.
        """
        cand_vec = self._vectorize_text(
            label_text,
            truncate=self.label_truncate,
            truncate_left=False,
            add_start=True,
            add_end=True,
        )

        # bsz x num cands x seq len
        cand_vec = cand_vec.unsqueeze(0).unsqueeze(0)
        _, _, cand_rep = self.model(cand_tokens=cand_vec)

        scores = self.model(
            ctxt_rep=self.ctxt[0], ctxt_rep_mask=self.ctxt[1], cand_rep=cand_rep
        )

        return scores

    def subsample_cands(self, subsamp):
        # Subsample the candidates
        print(
            " [ WARNING: Subsampling candidates for the acting "
            "score agent to {} total ]".format(subsamp)
        )
        # zip
        triples = list(
            zip(
                self.fixed_candidates,
                self.fixed_candidate_vecs,
                self.fixed_candidate_encs[0],
            )
        )
        # sample
        triples = random.sample(triples, subsamp)
        # separate
        cands, vecs, encs = zip(*triples)

        null_idx = self.NULL_IDX
        self.fixed_candidates = list(cands)
        self.fixed_candidate_vecs = padded_3d(
            [vecs], pad_idx=null_idx, dtype=vecs[0].dtype
        ).squeeze(0)
        self.fixed_candidate_encs = padded_3d(
            [encs], pad_idx=null_idx, dtype=encs[0].dtype
        )

    def _get_speaker_names(self):
        hist = self.history.get_history_str()
        partner_name = "_none_"
        self_name = "_none_"
        ind = hist.find("_partner_name")
        if ind != -1:
            partner_name = hist[hist.find("_partner_name") + len("_partner_name ") :]
            partner_name = partner_name[: partner_name.find("\n")]
        ind2 = hist.find("_self_name")
        if ind2 != -1:
            self_name = hist[hist.find("_self_name") + len("_self_name ") :]
            self_name = self_name[: self_name.find("\n")]
        base_self = self._block_utt_baseforms.get(self_name, self_name)
        base_partner = self._block_utt_baseforms.get(partner_name, partner_name)
        return self_name, partner_name, base_self, base_partner

    def _other_speaker_utt(self, c, self_name, partner_name, base_self, base_partner):
        # if self_name not in self._block_utt_given_partner.get(c, ''):
        #    return True
        if (
            c in self._block_utt_given_self
            and self_name in self._block_utt_given_self[c]
        ):
            return True
        if (
            c in self._block_utt_given_partner
            and partner_name in self._block_utt_given_partner[c]
        ):
            return True
        # check base forms, as well.
        if base_self != base_partner:
            for name in self._block_utt_given_self.get(c, []):
                if base_self == self._block_utt_baseforms.get(name, name):
                    if self._debug:
                        print("blocked on base!")
                    return True
            for name in self._block_utt_given_partner.get(c, []):
                if base_partner == self._block_utt_baseforms.get(name, name):
                    if self._debug:
                        print("blocked on base!")
                    return True
        return False

    def block_repeats(self, cand_preds, blocks=[]):
        """
        Heuristic to block a model repeating a line from the history.
        """
        if self.actingscore:
            # speed this up.
            return cand_preds

        ngram_sz = self.opt.get("block_ngrams", 0)
        max_seg_sz = ngram_sz + 1
        num_ngrams_blocked = 1

        self_name, partner_name, base_self, base_partner = self._get_speaker_names()
        history_strings = []
        history_ngrams = set()
        for h in self.history.history_raw_strings:
            # Heuristic: Block any given line in the history, splitting by '\n'.
            history_strings.extend(h.split("\n"))
            if ngram_sz > 0:
                ngrams = self.dict.tokenize(h.lower())
                for i in range(len(ngrams) - (ngram_sz - 1)):
                    ngram = ngrams[i : i + (ngram_sz - 1)]
                    history_ngrams.add(" ".join(ngram))
        for b in blocks:
            history_strings.extend(b)

        # Remove things in the history or have too much n-gram overlap.
        if ngram_sz > 0:
            new_preds = []
            for cp in cand_preds:
                np = []
                for c in cp:
                    if c in history_strings:
                        continue
                    ngrams = self.dict.tokenize(c.lower())
                    cnt = 0
                    for i in range(len(ngrams) - 2):
                        ngram = " ".join(ngrams[i : i + (ngram_sz - 1)])
                        if ngram in history_ngrams:
                            cnt += 1
                    # print(cnt, c)
                    if cnt > num_ngrams_blocked or len(ngrams) < max_seg_sz:
                        # print("blocked! ", c)
                        continue
                    np.append(c)
                new_preds.append(np)
            cand_preds = new_preds
            if len(cand_preds[0]) == 0:
                cand_preds[0].append("I don't know...")
        """
        Second heuristic: block any utterance by the other speaker
        Third heuristic: block any utterance said to me
            these are both in self._other_speaker_utt(x)
        """
        new_preds = []
        for cp in cand_preds:
            np = []
            npbonus = {}
            ind = 0
            for c in cp:
                ind += 1
                if self._debug:
                    newc = (
                        c
                        + "["
                        + str(self._block_utt_given_partner.get(c, "unknown"))
                        + "->"
                        + str(self._block_utt_given_self.get(c, "unknown"))
                        + "]"
                    )
                else:
                    newc = c
                if c not in history_strings and not self._other_speaker_utt(
                    c, self_name, partner_name, base_self, base_partner
                ):
                    bonus = 0
                    for cn in self._block_utt_given_partner.get(c, ""):
                        cname = self._block_utt_baseforms.get(cn, cn)
                        if base_self == cname and ind < self.opt.get(
                            "from_speaker_bonus", 20
                        ):
                            # print("special sadd:" + c, ind)
                            bonus += self.opt.get("from_speaker_bonus", 20) - ind
                    for cn in self._block_utt_given_self.get(c, ""):
                        cname = self._block_utt_baseforms.get(cn, cn)
                        if base_partner == cname and ind < self.opt.get(
                            "to_speaker_bonus", 20
                        ):
                            # print("special padd:" + c, ind)
                            bonus += self.opt.get("to_speaker_bonus", 20) - ind
                    if bonus > 0:
                        npbonus[newc] = bonus
                    else:
                        np.append(newc)
                else:
                    if self._debug:
                        print("blocked: " + newc)
            if len(np) == 0:
                if self._debug:
                    print("removed everything! oops.")
                np.append(cp[0])
            # sort bonus utterances and add to list.
            for s in sorted(npbonus.items(), key=lambda kv: (kv[1], kv[0])):
                np.insert(0, s[0])
                # if self._debug:
                #    print(s)

            new_preds.append(np)
        return new_preds
