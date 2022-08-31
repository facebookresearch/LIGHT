#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.world.souls.models.generative_heuristic_model_soul import (
    GenerativeHeuristicModelSoul,
)


class GenerativeHeuristicModelWithStartFeatureSoul(GenerativeHeuristicModelSoul):
    def add_startswith_tokens(self, context, dialogue_txt):
        # extract partner name
        partner_name = ""
        if self.target_node._last_interaction_partner_id != None:
            partner = self.world.oo_graph.get_node(
                self.target_node._last_interaction_partner_id
            )
        if partner is not None:
            partner_name = partner.get_prefix_view()
        if len(dialogue_txt) < 3:
            feature = "START " + partner_name
        else:
            feature = "CONTINUE " + partner_name
        final = context + dialogue_txt + "\n" + feature
        # print(final)
        return final

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
            is_safe = d[0][2]
            if not is_safe:
                # reset conversation when unsafe utterances are in the history
                dtxt = self.build_context(quest_txt)
        dtxt = dtxt.lstrip(" ")

        # Add starting context features, can help the model.
        final = self.add_startswith_tokens(txt, dtxt)

        return final
