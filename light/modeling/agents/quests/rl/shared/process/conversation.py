# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from collections import namedtuple
from light.graph.structured_graph import OOGraph
from light.world.world import World

Turn = namedtuple(
    "Turn",
    [
        "character",
        "context",
        "room_objects",
        "room_agents",
        "score",
        "available_actions",
        "carrying",
        "wearing",
        "wielding",
        "speech",
        "emote",
        "action",
    ],
)


class Conversation(object):
    def __init__(self, conv_dict, opt):
        """
        Initialize a Conversation object from a serialized dictionary (formatted as in
        jju/data/light/light_convs.pickle.pkl)

        :param conv_dict: Serialized dictionary wrapping a single conversation in the dataset
        """
        self.opt = opt

        # Create Agent-Specific Fields
        self.agents = [{"name": None, "persona": None} for _ in range(2)]

        # Create Setting-Specific Fields
        self.setting = {
            "name": None,
            "category": None,
            "description": None,
            "background": None,
        }

        # Create all Object Descriptions Dictionary
        self.all_descriptions = {}

        # Create Dialogue Turns
        self.turns = []

        # Parse Conversation Dictionary
        self.parse(conv_dict)

        # Error-Checking
        if len(self.turns) == 0:
            raise OverflowError

        # Unpack Turns into specific fields
        self.d = {
            Turn._fields[i]: list(zip(*self.turns))[i] for i in range(len(Turn._fields))
        }
        self.character, self.context = self.d["character"], self.d["context"]
        self.room_objects, self.room_agents = (
            self.d["room_objects"],
            self.d["room_agents"],
        )
        self.scores = self.d["score"]
        self.available_actions = self.d["available_actions"]
        self.carrying, self.wearing, self.wielding = (
            self.d["carrying"],
            self.d["wearing"],
            self.d["wielding"],
        )
        self.speech, self.emote, self.action = (
            self.d["speech"],
            self.d["emote"],
            self.d["action"],
        )

        assert (
            len(self.available_actions)
            == len(self.action)
            == len(self.speech)
            == len(self.emote)
        )

    def parse(self, conv_dict):
        """
        Parses out a conversation dict into the required Conversation fields

        :param conv_dict: Serialized conversation dictionary
        """
        # Get Graph
        g = OOGraph.from_json(conv_dict["graph_json"])
        world = World({}, None)
        world.oo_graph = g
        self.graph = world

        # Parse out information from dict representation
        conv_dict = conv_dict["conv_info"]
        acts, room, characters = (
            conv_dict["acts"],
            conv_dict["room"],
            conv_dict["characters"],
        )

        # Parse out Setting information
        self.setting["name"], self.setting["category"] = (
            room["setting"],
            room["category"],
        )
        self.setting["description"], self.setting["background"] = (
            room["description"],
            room["background"],
        )

        # Parse out Character Information - from @Jack, Persona used is personas[0]
        for i in range(2):
            self.agents[i]["name"] = characters[i][0][0]
            self.agents[i]["id"] = characters[i][0][1]
            self.agents[i]["persona"] = characters[i][1]["personas"][0]
            if "motivation" in characters[i][1].keys():
                self.agents[i]["motivation"] = characters[i][1]["motivation"]
            # self.agents[i]['persona'] = characters[i][1]['personas'][0]

        # Parse out Dialogue Information => Split into speech, emotes, and actions
        for turn in acts:
            speech, character, turn_data = (
                turn["text"],
                turn["id"],
                turn["task_data"],
            )
            action_emote, context = turn_data["action"], turn_data["text_context"]
            if "score" in turn.keys():
                score = turn["score"]
            else:
                score = 0.0

            r_obj, r_ag, available_actions = (
                turn_data["room_objects"],
                turn_data["room_agents"],
                turn_data["actions"],
            )
            carry, wear, wield = (
                turn_data["carrying"],
                turn_data["wearing"],
                turn_data["wielding"],
            )

            # Get object descriptions
            """for ob in r_obj + carry + wear + wield:
                obj_node = self.graph.desc_to_nodes(ob)
                description = self.graph.get_prop(obj_node[0], 'desc')

                if (
                    ob in self.all_descriptions
                    and self.all_descriptions[ob] != description
                ):
                    import IPython

                    IPython.embed()
                else:
                    self.all_descriptions[ob] = description"""

            # If action is an empty string, both action, emote are None
            """if len(action_emote) == 0:
                action, emote = None, None

            # If 'gesture' in action, then it is an emote
            elif 'gesture' in action_emote:
                action, emote = None, action_emote.split(' ')[1]

            # Otherwise, it's an action
            else:
                action, emote = action_emote, None"""
            emote = None
            action = turn_data["action"]

            # Append Turn object to turns
            # TODO remove emotes completely and parse stuff here
            self.turns.append(
                Turn(
                    character=character,
                    context=context,
                    room_objects=r_obj,
                    room_agents=r_ag,
                    score=score,
                    available_actions=available_actions,
                    carrying=carry,
                    wearing=wear,
                    wielding=wield,
                    speech=speech,
                    emote=emote,
                    action=action,
                )
            )
        # print(self.turns)

    def to_dict(self):
        return {
            "agents": self.agents,
            "setting": self.setting,
            "character": self.character,
            "context": self.context,
            "room_objects": self.room_objects,
            "room_agents": self.room_agents,
            "score": self.scores,
            "all_descriptions": self.all_descriptions,
            "available_actions": self.available_actions,
            "carrying": self.carrying,
            "wearing": self.wearing,
            "wielding": self.wielding,
            "speech": self.speech,
            "emote": self.emote,
            "action": self.action,
        }

    def use_feat(self, opt, field, ttype):
        if "all" in opt.get(field) or opt.get(field) == ttype:
            return True
        else:
            return False

    def convert_to_text(self, partner_idx):
        d = self.to_dict()
        d["self_agent"] = d["agents"][1 - partner_idx]
        d["partner_agent"] = d["agents"][partner_idx]

        text = ""
        # if self.opt['light_use_setting']:
        text += (
            "_setting_name "
            + d["setting"]["name"]
            # + ", "
            # + d['setting']['category']
            + "\n"
        )
        text += "_setting_desc " + d["setting"]["description"] + "\n"
        # if self.opt['light_use_person_names']:
        text += "_partner_name " + d["partner_agent"]["name"] + "\n"
        text += "_self_name " + d["self_agent"]["name"] + "\n"
        # if self.use_feat(self.opt, 'light_use_persona', 'self'):
        text += "_self_persona " + d["self_agent"]["persona"] + "\n"
        # if self.use_feat(self.opt, 'light_use_persona', 'other'):
        text += "_other_persona " + d["partner_agent"]["persona"] + "\n"
        if "motivation" in d["self_agent"].keys():
            text += "_self_motivation " + d["self_agent"]["motivation"] + "\n"
        if "motivation" in d["partner_agent"].keys():
            text += "_partner_motivation " + d["partner_agent"]["motivation"] + "\n"
        if self.opt["light_use_objects"]:
            for o, od in d["all_descriptions"].items():
                text += "_object_desc " + o + " : " + od + "\n"
        return d, text
