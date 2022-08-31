#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import os
from itertools import islice
import random

from parlai.agents.transformer.biencoder import BiencoderAgent
from parlai.agents.transformer.polyencoder import PolyencoderAgent
from parlai.agents.transformer.generator import GeneratorAgent
from parlai.core.opt import Opt

from parlai.core.torch_agent import Output
from parlai.utils.misc import warn_once
from parlai.utils.torch import padded_3d
from parlai.core.metrics import AverageMetric


class LightPolyencoderAgent(PolyencoderAgent):
    def __init__(self, opt: Opt, shared=None):
        super().__init__(opt, shared)

    """def score_candidates(self, batch, cand_vecs, cand_encs=None):
        # convoluted check that not all memories are empty
        if (
            self.opt['use_memories']
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

        return scores"""

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
                """if os.path.isfile(self.opt['fixed_candidate_vecs']):
                    vecs_path = opt['fixed_candidate_vecs']
                    vecs = self.load_candidates(vecs_path)
                else:"""
                setting = self.opt["fixed_candidate_vecs"]
                model_dir, model_file = os.path.split(self.opt["model_file"])
                model_name = os.path.splitext(model_file)[0]
                cands_name = os.path.splitext(os.path.basename(cand_path))[0]
                vecs_path = os.path.join(
                    self.opt["path"], ".".join([cands_name, "vecs"])
                )
                if self.opt["eval_mode"] == "test":  # and os.path.isfile(vecs_path):
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
                        self.opt["path"], ".".join([cands_name, "encs"])
                    )
                    if self.opt["eval_mode"] == "test":
                        encs = self.load_candidates(enc_path, cand_type="encodings")
                    else:
                        encs = self._make_candidate_encs(self.fixed_candidate_vecs)
                        self._save_candidates(
                            encs, path=enc_path, cand_type="encodings"
                        )

                    # if setting == 'reuse' and os.path.isfile(enc_path):
                    #    encs = self.load_candidates(enc_path, cand_type='encodings')
                    # else:
                    # encs = self._make_candidate_encs(
                    #     self.fixed_candidate_vecs, path=enc_path
                    # )
                    # self._save_candidates(
                    #    encs, path=enc_path, cand_type='encodings'
                    # )
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


class LightBiencoderAgent(BiencoderAgent):
    def __init__(self, opt: Opt, shared=None):
        super().__init__(opt, shared)

    """def score_candidates(self, batch, cand_vecs, cand_encs=None):
        # convoluted check that not all memories are empty
        if (
            self.opt['use_memories']
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

        return scores"""

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
                """if os.path.isfile(self.opt['fixed_candidate_vecs']):
                    vecs_path = opt['fixed_candidate_vecs']
                    vecs = self.load_candidates(vecs_path)
                else:"""
                setting = self.opt["fixed_candidate_vecs"]
                model_dir, model_file = os.path.split(self.opt["model_file"])
                model_name = os.path.splitext(model_file)[0]
                cands_name = os.path.splitext(os.path.basename(cand_path))[0]
                vecs_path = os.path.join(
                    self.opt["path"], ".".join([cands_name, "vecs"])
                )
                if self.opt["eval_mode"] == "test":  # and os.path.isfile(vecs_path):
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
                        self.opt["path"], ".".join([cands_name, "encs"])
                    )
                    if self.opt["eval_mode"] == "test":
                        encs = self.load_candidates(enc_path, cand_type="encodings")
                    else:
                        encs = self._make_candidate_encs(self.fixed_candidate_vecs)
                        self._save_candidates(
                            encs, path=enc_path, cand_type="encodings"
                        )

                    # if setting == 'reuse' and os.path.isfile(enc_path):
                    #    encs = self.load_candidates(enc_path, cand_type='encodings')
                    # else:
                    # encs = self._make_candidate_encs(
                    #     self.fixed_candidate_vecs, path=enc_path
                    # )
                    # self._save_candidates(
                    #    encs, path=enc_path, cand_type='encodings'
                    # )
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


class LightGeneratorAgent(GeneratorAgent):
    def __init__(self, opt: Opt, shared=None):
        # TODO overwrite history here
        super().__init__(opt, shared)
