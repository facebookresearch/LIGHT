#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import pickle


class ConversationCheckpointParser:
    """
    Loads conversations from a pickle file and contains methods to query the
    number of conversations and other metrics.
    """

    def __init__(self, pkl_lst_path):
        with open(pkl_lst_path, "rb") as f:
            conv_lst = pickle.load(f)
        self.conv_lst = conv_lst

    def count_conversations(self):
        return len(self.conv)

    def get_average_conversation_length(self):
        lengths = [len(i) for i in self.conv]
        return sum(lengths) / len(lengths)

    def get_total_utterances(self):
        return self.count_conversations() * self.get_average_conversation_length()

    def get_room_pickle_id(self, index):
        """
        Returns the room ID in the pickle file of a particular conversation.
        """
        conv = self.conv_lst[index]
        room_pickle_id = conv["conv_info"]["room"]["id"]
        return room_pickle_id

    def get_graph(self, index):
        conv = self.conv_lst[index]
        graph = conv["graph"]
        return graph

    def name_to_persona(self, index):
        """
        Returns a dictionary that maps the name of a character to the persona
        of the character in a particular conversation.
        """
        conv_raw = self.conv_lst[index]
        conv = conv_raw["conv_info"]["acts"]
        chars_lst = conv_raw["conv_info"]["characters"]
        char_dict = {}
        for i in range(min(len(conv), len(chars_lst))):
            char_name = chars_lst[i][0]
            char_dict[char_name.lower()] = conv[i]["task_data"]["persona"]
        return char_dict

    def get_conv_data(self, index):
        """
        Returns turn data by all speakers in a specific conversation.
        Index refers to the index of the converstaion in the pickle passed to
        the class. Returns information needed to create an entry in turns_table
        """
        conv = self.conv_lst[index]["conv_info"]["acts"]
        char_dict = self.name_to_persona(index)
        data = []
        for i in range(len(conv)):
            action = conv[i]["task_data"]["action"]
            if action[:8] == "gesture ":
                action_type = "emote"
                action_text = action[8:]
                action_return = (action_type, action_text)
            elif action != "":
                action_type = "action"
                action_text = action
                action_return = (action_type, action_text)
            else:
                action_return = None
            speaker_name = conv[i]["id"].lower()
            if len(char_dict) == 1:
                listener_name = None
            else:
                temp_lst = list(char_dict.keys())
                temp_lst.remove(speaker_name)
                listener_name = temp_lst[0]
            data.append(
                {
                    "speaker": speaker_name,
                    "listener": listener_name,
                    "text": conv[i]["text"],
                    "action": action_return,
                    "duration": conv[i]["duration"],
                }
            )
        return data

    def get_convs_data(self):
        result = []
        for i in range(len(self.conv_lst)):
            result.append((self.get_room_pickle_id(i), self.get_conv_data(i)))
        return result
