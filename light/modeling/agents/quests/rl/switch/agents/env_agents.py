#!/usr/bin/env python3


from light.modeling.agents.quests.rl.shared.process.constants import *

from light.modeling.agents.quests.rl.shared.environments.history import (
    GoalOrientedHistory,
)
from light.modeling.agents.quests.rl.switch.models.transformer import (
    LightPolyencoderAgent,
)

from parlai.core.torch_agent import Output, Batch
from parlai.utils.torch import padded_3d
import torch
import json
import random


class LightDMAgent(LightPolyencoderAgent):
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

    def set_p2_tok(self, p2_tok):
        self.history.p2_token = p2_tok

    def block_repeats(self, cand_preds, batch):
        """Heuristic to block a model repeating a line from the history.
        Edited from TRA's block repeats
        """
        if batch is None:
            return super().block_repeats(cand_preds)
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

    def self_observe(self, self_message, p2_tok=None):
        if p2_tok:
            self.history.p2_token = p2_tok
        return super().self_observe()

    def __init__(self, opt, shared=None):
        super().__init__(opt, shared)
        # load agent speak stop list.
        fnames = [
            opt.get(
                "partner_trainset",
                "/checkpoint/light/projects/dialog/agent_to_utterance_partner_trainset.txt",
            ),
            opt.get(
                "trainset",
                "/checkpoint/light/projects/dialog/agent_to_utterance_trainset.txt",
            ),
        ]
        self._debug = False
        self.actingscore = True
        self.boring_alpha = self.opt["boring_alpha"]
        if shared is not None and "block_utt_given_self" in shared:
            self._block_utt_given_self = shared["block_utt_given_self"]
            self._block_utt_given_partner = shared["block_utt_given_partner"]
            self._block_utt_baseforms = shared["block_utt_baseforms"]
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
                            if utt not in self._block_utt_given_self:
                                self._block_utt_given_self[utt] = []
                            self._block_utt_given_self[utt].append(name)
                        else:
                            if utt not in self._block_utt_given_partner:
                                self._block_utt_given_partner[utt] = []
                            self._block_utt_given_partner[utt].append(name)

    def share(self):
        s = super().share()
        s["block_utt_given_self"] = self._block_utt_given_self
        s["block_utt_given_partner"] = self._block_utt_given_partner
        s["block_utt_baseforms"] = self._block_utt_baseforms
        return s

    def score_candidates(self, batch, cand_vecs, cand_encs=None, scores_only=False):
        """
        This is an override from the polyencoder function in order to cache
        the context representation in the case of `self.actingscore`.
        """
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
                    "If you don",
                    "I'd rather be in the forest so don",
                    "i don",
                    "I don not know.",
                    "I was just in the",
                    "ill just that",
                    "I i uh i cant",
                    "I can here you, and if don't back off i'll deal with you",
                    "You",
                    "No",
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
                    vs[0][i] = 100000  # don't use
            print("[done!]")
            self.boring = vs

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

    def score_one_candidate(self, batch):
        """
        Score one label using previous cached context.

        This is typically only used by the acting score agent,
        so that we can pre-comute the score of the fixed candidates
        given the context, and the compute the score of the human's
        message using the cached context.
        """
        batch = self.batchify(batch)

        cands, cand_vecs, label_inds = self._build_candidates(
            batch, source="inline", mode="eval"
        )
        bsz = self._get_batch_size(batch)
        # ctxt_rep, ctxt_rep_mask, _ = self.model(**self._model_context_input(batch))

        _, _, cand_rep = self.model(cand_tokens=cand_vecs)
        # num_cands = cand_rep.size(0)  # will be bsz if using batch cands
        # cand_rep = cand_rep.expand(num_cands, bsz, -1).transpose(0, 1).contiguous()

        scores = self.model(
            ctxt_rep=self.ctxt[0], ctxt_rep_mask=self.ctxt[1], cand_rep=cand_rep
        )
        # bsz x num cands x seq len
        # cand_vec = cand_vec.unsqueeze(0)#.unsqueeze(0)
        # _, _, cand_rep = self.model(cand_tokens=cand_vec)

        # scores = self.model(
        #    ctxt_rep=self.ctxt[0], ctxt_rep_mask=self.ctxt[1], cand_rep=cand_rep
        # )

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

    def block_repeats(self, cand_preds):
        """
        Heuristic to block a model repeating a line from the history.
        """
        if self.actingscore:
            # speed this up.
            return cand_preds

        self_name, partner_name, base_self, base_partner = self._get_speaker_names()
        history_strings = []
        for h in self.history.history_raw_strings:
            # Heuristic: Block any given line in the history, splitting by '\n'.
            history_strings.extend(h.split("\n"))
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
                            bonus += self.opt.get("from_speaker_bonus", 20) - ind
                    for cn in self._block_utt_given_self.get(c, ""):
                        cname = self._block_utt_baseforms.get(cn, cn)
                        if base_partner == cname and ind < self.opt.get(
                            "to_speaker_bonus", 20
                        ):
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

            new_preds.append(np)
        return new_preds


class LightRetrievalAgent(LightPolyencoderAgent):
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

    def set_p2_tok(self, p2_tok):
        self.history.p2_token = p2_tok

    def block_repeats(self, cand_preds, batch):
        """Heuristic to block a model repeating a line from the history.
        Edited from TRA's block repeats
        """
        if batch is None:
            return super().block_repeats(cand_preds)
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

    def self_observe(self, self_message, p2_tok=None):
        if p2_tok:
            self.history.p2_token = p2_tok
        return super().self_observe()


# TODO Add generator agent w/ env wrapper here
