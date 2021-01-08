#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.world.souls.soul import Soul
from copy import deepcopy
import os
import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.graph.world.world import World
    from light.graph.events.base import GraphEvent


class BaseSoul(Soul):
    """
    Base soul that both player and NPC souls can inherit.
    It does some basic things like conversation interaction partner and dialogue
    and action history trackin, and roleplaying scoring, which is useful for both.
    """

    def __init__(self, target_node: "GraphAgent", world: "World"):
        """
        Standard Initialization.
        """
        super().__init__(target_node, world)
        self.target_node._last_interaction_partner_id = None
        self.reset_interaction_history(self.target_node)
        
    def get_last_interaction_partner(self, node=None):
        if node == None:
            node = self.target_node
        return node._last_interaction_partner_id

    def log_interaction_from_event(self, event):
        event_name = event.__class__.__name__
        agent = self.target_node
        agent_id = agent.node_id
        partner_id = self.target_node._last_interaction_partner_id
        event_actor_id = event.actor.node_id
        if (agent_id == event_actor_id or partner_id == event_actor_id) and (
            event_name == "TellEvent"
            or event_name == "SayEvent"
            or event_name == "WhisperEvent"
        ):
            # log event
            text = event.text_content
            if not (text.startswith("DEBUG")):
                agent._last_interaction_history.append(
                    [(event_actor_id, event_name), text]
                )
        if (agent_id == event_actor_id or partner_id == event_actor_id) and (
            event_name == "EmoteEvent"
        ):
            # log event
            text = event.text_content
            agent._last_interaction_history.append(
                [(event_actor_id, event_name), "*" + text + "*"]
            )
        # Only log these kind of act events.
        act_events = [
            "UnfollowEvent",
            "FollowEvent",
            "UnblockEvent",
            "BlockEvent",
            "HitEvent",
            "HugEvent",
            "GetObjectEvent",
            "PutObjectInEvent",
            "DropObjectEvent",
            "StealObjectEvent",
            "GiveObjectEvent",
            "EquipObjectEvent",
            "WearEvent",
            "WieldEvent",
            "RemoveObjectEvent",
            "IngestEvent",
            "EatEvent",
            "DrinkEvent",
            "ExamineEvent",
            "UseEvent",
        ]
        if (agent_id == event_actor_id or partner_id == event_actor_id) and (
            event_name in act_events
        ):
            # log event
            text = event.to_canonical_form()
            # import pdb; pdb.set_trace()
            agent._last_interaction_history.append(
                [(event_actor_id, event_name), "*" + text + "*"]
            )

    def set_interaction_partners_from_event(self, event):
        # Calculate who the event involves.
        agent1 = event.actor
        agent2 = None
        for n in event.target_nodes:
            if n.agent:
                agent2 = n

        # We need to assign partners for Say events.
        if event.__class__.__name__ == "SayEvent":
            # We need to predict who is talking to each other.
            if not hasattr(agent1, "_last_interaction_partner_id"):
                agent1._last_interaction_partner_id = None
            if agent1._last_interaction_partner_id is not None:
                agent2 = self.world.oo_graph.get_node(
                    agent1._last_interaction_partner_id
                )
                if agent1.get_room() != agent2.get_room():
                    agent1._last_interaction_partner_id = None
                    agent2._last_interaction_partner_id = None
                    agent2 = None
            if agent2 is None:
                # Now find a partner if available (someone in the room who isn't engaged).
                for n in agent1.get_room().get_contents():
                    if n.agent and n != agent1:
                        if (
                            not hasattr(n, "_last_interaction_partner_id")
                            or n._last_interaction_partner_id == None
                        ):
                            # Assign this agent.
                            agent2 = n

        # Now set the values given the two agents (if we have found two agents).
        if agent2 is not None:
            self.dialogue_switch_partner(agent1, agent2)

    def reset_interaction_history(self, agent=None):
        if agent == None:
            agent = self.target_node

        agent._last_interaction_partner_id = None
        agent._last_interaction_history = []

    def dialogue_switch_partner(self, agent1, agent2):
        """
        Clear this Soul's set dialogue partner, possibly clearing
        the partner if they still point to it.
        """
        if not hasattr(agent1, "_last_interaction_partner_id"):
            self.reset_interaction_history(agent1)
        if not hasattr(agent2, "_last_interaction_partner_id"):
            self.reset_interaction_history(agent2)

        if agent1._last_interaction_partner_id == agent2.node_id:
            return  # already interacting.

        if agent1._last_interaction_partner_id is not None:
            agent3 = self.world.oo_graph.get_node(agent1._last_interaction_partner_id)
            self.reset_interaction_history(agent3)
        if agent2._last_interaction_partner_id is not None:
            agent4 = self.world.oo_graph.get_node(agent2._last_interaction_partner_id)
            self.reset_interaction_history(agent4)

        self.reset_interaction_history(agent1)
        self.reset_interaction_history(agent2)
        agent1._last_interaction_partner_id = agent2.node_id
        agent2._last_interaction_partner_id = agent1.node_id
        # if hasattr(self.world, 'debug'):
        #    print(str(agent1) + " started interaction with " + str(agent2))

    def build_context(self, partner_name=None, quest_txt=None):
        """
        Build the full context for this Soul's model
        """
        agent = self.target_node
        room = agent.get_room()
        txt += "_setting_name " + room.name + "\n"
        txt += "_setting_desc " + room.desc + "\n"
        if partner_name is not None:
            txt += "_partner_name " + partner_name + "\n"
        else:
            if self.target_node._last_interaction_partner_id != None:
                partner = self.world.oo_graph.get_node(
                    self.target_node._last_interaction_partner_id
                )
                if partner is not None:
                    txt += "_partner_name " + partner.get_prefix_view() + "\n"
        txt += "_self_name " + agent.name + "\n"
        txt += "_self_persona " + agent.persona
        if quest_txt is not None:
            txt += quest_text
        txt += "\n"
        return txt

    def build_dialog_context(self, quest_txt=None):
        # Initial context.
        txt = self.build_context(quest_txt)
        # Dialogue/interaction context.
        dtxt = ""
        agent = self.target_node
        agent_id = agent.node_id
        turn_id = None
        for d in agent._last_interaction_history:
            current_turn_id = d[0][0]
            if turn_id == None or turn_id == current_turn_id:
                dtxt += " " + d[1]
            else:
                dtxt = dtxt.lstrip(" ")
                dtxt += "\n" + d[1]
            turn_id = current_turn_id
        return txt + dtxt

    ## ----- ROLE PLAYING SCORE FUNCTIONS BELOW

    @classmethod
    def load_roleplaying_score_model(cls, roleplaying_score_model_file):
        """
        Load up and create shared roleplaying score model for use with this class
        """
        # TODO refactor with some kind of model-loading standard for model souls?
        from parlai.core.params import ParlaiParser
        from parlai.core.agents import create_agent

        parser = ParlaiParser(True, True, "")
        args = ["-mf", roleplaying_score_model_file]
        opt, _unknown = parser.parse_and_process_known_args(args=args)
        # opt["interactive_mode"] = True
        # return create_agent(opt, requireModelExists=True)
        print("[ Creating roleplaying score agent ... ]")
        model_opt = {}
        model_opt["datapath"] = opt["datapath"]
        model_opt["model_file"] = roleplaying_score_model_file
        # '/checkpoint/jase/projects/light/beatthehobbot/swp6_light_bi/actmodelv2/model'
        # model_opt['fixed_candidates_path'] = ranker_agent.opt['fixed_candidates_path']
        model_opt["candidates"] = "fixed"
        model_opt["eval_candidates"] = "fixed"
        model_opt["no_cuda"] = True
        model_opt["use_reply"] = "none"
        model_opt["interactive_mode"] = True
        model_opt["boring_alpha"] = 0
        model_opt["override"] = deepcopy(model_opt)
        roleplaying_score_model = create_agent(model_opt)
        roleplaying_score_model.boring = None

        # mark this agent as the special RP score agent
        roleplaying_score_model.actingscore = True
        # override eval step here
        roleplaying_score_model.eval_step = roleplaying_score_model.eval_step_scoresonly
        return roleplaying_score_model

    def too_much_string_overlap(self, s1, s2):
        """
        Check if strings overlap too much.
        """
        s1_words = set(s1.split())
        s2_words = set(s2.split())
        if len(s2_words) == 0:
            return False
        overlap = len(s1_words.intersection(s2_words))
        if overlap / len(s2_words) > 0.5 or (len(s2_words) < 5 and overlap >= 2):
            return True
        return False

    def get_fixed_cand_scores(self, context):
        """
        Returns the candidates at self.SAMPLE_INDS
        """
        self.roleplaying_score_model.opt["eval_candidates"] = "fixed"
        self.roleplaying_score_model.eval_candidates = "fixed"  # set candidates
        act = {
            "text": context,
            "id": "persona",
            "episode_done": False,
        }
        self.roleplaying_score_model.reset()
        self.roleplaying_score_model.observe(deepcopy(act))
        _ = self.roleplaying_score_model.act()
        return self.roleplaying_score_model.scores

    def get_pos_human_msg(self, human_msg, scores):
        """
        Get the model score of the human message and compare to fixed cands.
        """
        human_score = float(self.roleplaying_score_model.score_one_candidate(human_msg))
        human_rank = int((scores > human_score).sum())
        return human_rank, human_score

    def score_conversation(self):
        if not hasattr(self, "roleplaying_score_model"):
            return 0

        context1 = self.build_dialog_context()
        # print(context)
        contextsplit = context1.split("\n")
        context = "\n".join(contextsplit[:-1])
        human_msg = contextsplit[-1]
        if len(human_msg.split()) < 5:
            return 0
        # check for n-gram match with context
        if self.too_much_string_overlap(context, human_msg):
            return 0
        # mark this agent as the special RP score agent
        self.roleplaying_score_model.actingscore = True
        # override eval step here
        self.roleplaying_score_model.eval_step = (
            self.roleplaying_score_model.eval_step_scoresonly
        )
        fixed_cand_scores = self.get_fixed_cand_scores(context)
        pos, score = self.get_pos_human_msg(human_msg, fixed_cand_scores)
        # print("pos:", pos)
        if pos < 1000:
            final_score = 4
        elif pos < 2000:
            final_score = 3
        elif pos < 5000:
            final_score = 2
        elif pos < 10000:
            final_score = 1
        else:
            final_score = 0
        return final_score

    def role_playing_score_events(self, event):
        # Track event history, and award roleplaying score if appropriate.
        agent = event.actor
        if agent != self.target_node:
            return  # only for self actions
        if (
            event.__class__.__name__ == "SayEvent"
            or event.__class__.__name__ == "TellEvent"
        ):
            if agent._last_interaction_partner_id != None:
                agent2_id = agent._last_interaction_partner_id
                if not hasattr(agent, "_agent_interactions"):
                    agent._agent_interactions = {}
                if not hasattr(agent, "xp"):
                    agent.xp = 0
                if agent2_id not in agent._agent_interactions:
                    agent._agent_interactions[agent2_id] = 0

                stars = self.score_conversation()
                agent._agent_interactions[agent2_id] += stars
                agent.xp += stars
                # Send star score message.
                if stars > 0:
                    self.world.send_msg(
                        agent.node_id, "(You gained " + str(stars) + " XP!)"
                    )
                # if hasattr(self.world, 'debug'):
                #    print(str(agent) +" score: " + str(agent._agent_interactions[agent2_id]))
