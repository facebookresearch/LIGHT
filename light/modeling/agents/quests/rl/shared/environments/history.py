#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from parlai.core.torch_agent import History

from collections import deque
from light.modeling.agents.quests.rl.shared.process.constants import *


class QuestHistory(object):
    """
    History handles tracking the dialogue state over the course of an episode.

    History may also be used to track the history of any field.

    :param field:
        field in the observation to track over the course of the episode
        (defaults to 'text')

    :param vec_type:
        specify a 'list' or 'deque' to save the history in this object

    :param maxlen:
        if `vec_type` is 'deque', this sets the maximum length of that object

    :param p1_token:
        token indicating 'person 1'; opt must have 'person_tokens' set to True
        for this to be added

    :param p1_token:
        token indicating 'person 2'; opt must have 'person_tokens' set to True
        for this to be added

    :param dict_agent:
        DictionaryAgent object for tokenizing the history
    """

    def __init__(
        self,
        opt,
        field="text",
        vec_type="deque",
        maxlen=None,
        size=-1,
        p1_token="__p1__",
        p2_token="__p2__",
        dict_agent=None,
    ):
        self.field = field
        self.dict = dict_agent
        self.delimiter = opt.get("delimiter", "\n")
        self.delimiter_tok = self.parse(self.delimiter)
        self.size = size
        self.split_on_newln = opt.get("split_lines", False)
        self._global_end_token = opt.get("history_add_global_end_token", None)
        if self._global_end_token is not None:
            self._global_end_token = self.dict[self.dict.end_token]

        # set up history objects
        if vec_type != "deque" and vec_type != "list":
            raise RuntimeError("Type {} is not supported for history".format(vec_type))
        self.vec_type = vec_type
        self.max_len = maxlen

        self.history_strings = []
        self.history_raw_strings = []
        self.history_vecs = []
        self.temp_history = None

        # person token args
        self.add_person_tokens = opt.get("person_tokens", False)
        self.add_p1_after_newln = opt.get("add_p1_after_newln", False)
        self.p1_token = p1_token
        self.p2_token = p2_token

    def parse(self, text):
        """
        Tokenize text with the given dictionary.
        """
        return self.dict.txt2vec(text)

    def reset(self):
        """
        Clear the history.
        """
        self.history_raw_strings = []
        self.history_strings = []
        self.history_vecs = []

    def _update_strings(self, text):
        if self.size > 0:
            while len(self.history_strings) >= self.size:
                self.history_strings.pop(0)
        self.history_strings.append(text)

    def _update_raw_strings(self, text):
        if self.size > 0:
            while len(self.history_raw_strings) >= self.size:
                self.history_raw_strings.pop(0)
        self.history_raw_strings.append(text)

    def _update_vecs(self, text):
        if self.size > 0:
            while len(self.history_vecs) >= self.size:
                self.history_vecs.pop(0)
        self.history_vecs.append(self.parse(text))

    def add_reply(self, text):
        """
        Add your own response to the history.
        """
        self._update_raw_strings(text)
        if self.add_person_tokens:
            text = self._add_person_tokens(text, self.p2_token)
        # update history string
        self._update_strings(text)
        # update history vecs
        self._update_vecs(text)

    def update_history(self, obs, temp_history=None):
        """
        Update the history with the given observation.

        param obs:     Observation used to update the history. param temp_history:
        Optional temporary string. If it is not None,     this string will be appended
        to the end of the     history. It will not be in the history on the     next
        dialogue turn. Set to None to stop adding     to the history.
        """
        if self.field in obs and obs[self.field] is not None:
            if self.split_on_newln:
                next_texts = obs[self.field].split("\n")
            else:
                next_texts = [obs[self.field]]
            for text in next_texts:
                self._update_raw_strings(text)
                if self.add_person_tokens:
                    text = self._add_person_tokens(
                        obs[self.field], self.p1_token, self.add_p1_after_newln
                    )
                # update history string
                self._update_strings(text)
                # update history vecs
                self._update_vecs(text)

        self.temp_history = temp_history

    def get_history_str(self):
        """
        Return the string version of the history.
        """
        if len(self.history_strings) > 0:
            history = self.delimiter.join(self.history_strings)
            if self.temp_history is not None:
                history = self.temp_history + history
            return history

        return None

    def get_history_vec(self):
        """
        Return a vectorized version of the history.
        """
        if len(self.history_vecs) == 0:
            return None

        if self.vec_type == "deque":
            history = deque(maxlen=self.max_len)
            for vec in self.history_vecs[:-1]:
                history.extend(vec)
                history.extend(self.delimiter_tok)
            history.extend(self.history_vecs[-1])
            if self.temp_history is not None:
                # history.extend(self.parse(self.temp_history))
                history.extendleft(self.parse(self.temp_history))
            if self._global_end_token is not None:
                history.extend([self._global_end_token])
        else:
            # vec type is a list
            history = []
            for vec in self.history_vecs[:-1]:
                history += vec
                history += self.delimiter_tok
            history += self.history_vecs[-1]
            if self.temp_history is not None:
                history.extend(self.parse(self.temp_history))
            if self._global_end_token is not None:
                history += [self._global_end_token]

        return history

    def get_history_vec_list(self):
        """
        Return a list of history vecs.
        """
        return self.history_vecs

    def _add_person_tokens(self, text, token, add_after_newln=False):
        if add_after_newln:
            split = text.split("\n")
            split[-1] = token + " " + split[-1]
            return "\n".join(split)
        else:
            return token + " " + text


class GoalOrientedHistory(QuestHistory):
    def __init__(self, opt, text_truncate, histsz, P1_TOKEN, P2_TOKEN, dictionary, tag):
        super().__init__(
            opt,
            maxlen=text_truncate,
            size=histsz,
            p1_token=P1_TOKEN,
            p2_token=P2_TOKEN,
            dict_agent=dictionary,
        )
        self.dictionary = dictionary
        self.tag = tag
        self.tag_vec = self.parse(tag)
        self.reset_p1_tok = self.p1_token
        self.goal = None
        self.goal_vec = None
        self.cluster = None
        self.cluster_vec = None
        self.context = None

    def set_context(self, context):
        self.context = context

    def set_goal(self, goal):
        # self.dictionary
        goal_str = ""
        for atype in ALL_ATYPES:
            if atype in goal:
                goal_str += FUTURE_PARTNER_TAG[atype] + " " + goal[atype]
        self.goal = goal_str
        self.goal_vec = self.parse(goal_str)

    def set_cluster(self, cluster):
        self.cluster = cluster
        self.cluster_vec = self.parse(cluster)

    # def add_reply(self, text):
    #     """
    #     Add your own response to the history.
    #     """
    #     self._update_raw_strings(text)
    #     if self.add_person_tokens:
    #         text = self._add_person_tokens(text, self.p2_token)
    #     # update history string
    #     self._update_strings(text)
    #     # update history vecs
    #     self._update_vecs(text)

    def update_history(self, obs, add_next=None, temp_history=None):
        # TODO MESS WITH STUFF HERE SO THAT SETTING (IN THIS CASE SELF.GOAL IS AT THE FRONT OF THE STRING REGARDLESS
        self.p1_token = self.reset_p1_tok
        ignore_person_tokens = obs.get("ignore_person_tokens", False)
        if ignore_person_tokens:
            self.add_person_tokens = False
        else:
            self.add_person_tokens = True
            if obs.get("p1_token", False):
                self.p1_token = obs.get("p1_token")
        if obs.get("tag_token"):
            self.tag = obs["tag_token"]
            self.tag_vec = self.parse(obs["tag_token"])
        # obs['text'] = self.context + obs['text']
        return super().update_history(obs, temp_history=self.context)

    '''def get_history_str(self):
        """Return the string version of the history."""
        if len(self.history_strings) > 0:
            history = self.history_strings + [self.tag]
            if self.goal:
                history += [self.goal]
            if self.cluster:
                history += [self.cluster]
            if self.context:
                history += [self.context]
            return self.delimiter.join(history) + '\n'
        return None'''

    '''def get_history_vec(self):
        """Return a vectorized version of the history."""
        if len(self.history_vecs) == 0:
            return None

        if self.vec_type == 'deque':
            history = deque(maxlen=self.max_len)
            for vec in self.history_vecs:
                history.extend(vec)
                history.extend(self.delimiter_tok)
            history.extend(self.tag_vec)
            if self.goal_vec is not None:
                history.extend(self.delimiter_tok)
                history.extend(self.goal_vec)
            if self.cluster_vec is not None:
                history.extend(self.delimiter_tok)
                history.extend(self.cluster_vec)
        else:
            # vec type is a list
            history = []
            for vec in self.history_vecs:
                history += vec
                history += self.delimiter_tok
            history += self.tag_vec
            if self.goal_vec is not None:
                history += self.delimiter_tok
                history += self.goal_vec
            if self.cluster_vec is not None:
                history += self.delimiter_tok
                history += self.goal_vec

        return history'''
