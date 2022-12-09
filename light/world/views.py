#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from collections import Counter
import emoji

from light.graph.utils import rm, deprecated
from light.graph.elements.graph_nodes import GraphRoom


NUMS_ARRAY = [
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "a lot of",
]

HEALTH_TUPLES = [
    ("pretty dead", -1),
    ("on the verge of death", -1),
    ("very weak", -1),
    ("weak", -1),
    ("ok", 1),
    ("good", 1),
    ("strong", 1),
    ("very strong", 1),
    ("nigh on invincible", 1),
]


class WorldViewer(object):
    """Contains methods related to converting game state into viewable and
    consumable text"""

    def __init__(self, world):
        self.world = world
        self.debug = world.debug

    # TODO maybe consider item viewers instead? world view is rare
    # deinitely try to move to versions that use the node rather than the id

    def get_inventory_text_for(self, id, give_empty=True):
        """Get a description of what id is carrying or equipped with"""
        world = self.world
        s = ""
        carry_ids = []
        wear_ids = []
        wield_ids = []
        for o in world.node_contains(id):
            if world.get_prop(o, "equipped"):
                if world.get_prop(o, "wearable"):
                    wear_ids.append(o)
                elif world.get_prop(o, "wieldable"):
                    wield_ids.append(o)
            else:
                carry_ids.append(o)
        if len(carry_ids) + len(wield_ids) + len(wear_ids) == 0:
            if not give_empty:
                return ""

        if len(carry_ids) == 0:
            s += "carrying nothing"
        else:
            s += "carrying " + self.display_node_list_id(carry_ids)
        if len(wear_ids) > 0:
            s += ", "
            if len(wield_ids) == 0:
                s += "and "
            s += "wearing " + self.display_node_list_id(wear_ids)
        if len(wield_ids) > 0:
            s += ", and wielding " + self.display_node_list_id(wield_ids)
        return s + "."

    def get_health_text_for(self, id):
        """Return the text description of someone's numeric health"""
        # TODO get the correct values
        health = self.world.oo_graph.get_node(id).get_prop("health")
        if health < 0:
            health = 0
        if health is None or health is False:
            health = 1
        if health > 8:
            health = 8
        # Second argument indicates sentiment (can use for descriptions).
        return HEALTH_TUPLES[int(health)][0], HEALTH_TUPLES[int(health)][1]

    def get_node_desc(self, node, from_node=None, use_the=False, drop_prefix=False):
        """Return a viewable description for this node in the graph"""
        if from_node is not None:
            # A description of something (right now, a location)
            # from another location.
            # This gets the description from the path edge.
            path_desc = self.path_to_desc(node, from_node)
            if path_desc is not False:
                if path_desc.startswith("the") or path_desc.startswith("a"):
                    return path_desc
                return "the " + path_desc

        world = self.world
        ent = node.name
        if node.get_prop("capitalize", False) is True:
            ent = ent.capitalize()
        if node.get_prop("dead"):
            ent = "dead " + ent
        if node.get_prop("player_name"):
            ent = node.get_prop("player_name")
        elif node.get_prop("agent") or node.get_prop("object"):
            prefix = self.name_prefix(node, ent, use_the)
            if prefix != "" and not drop_prefix:
                # -- clean up data, TODO: shouldn't need this?
                if ent.lower().startswith("a "):
                    ent = ent[2:]
                if ent.lower().startswith("an "):
                    ent = ent[3:]
                if ent.lower().startswith("the "):
                    ent = ent[4:]
                # ---- end clean up --------------
                ent = prefix + " " + ent
        elif node.get_prop("room"):
            prefix = self.name_prefix(node, ent, use_the)
            if prefix != "":
                ent = prefix + " " + ent
            else:
                ent = "the " + ent
        return ent

    @deprecated
    def get_node_desc_id(self, id, from_id=False, use_the=False, drop_prefix=False):
        """Return a viewable description for this node in the graph"""
        if from_id:
            # A description of something (right now, a location)
            # from another location.
            # This gets the description from the path edge.
            path_desc = self.path_to_desc_id(id, from_id)
            if path_desc is not False:
                if path_desc.startswith("the") or path_desc.startswith("a"):
                    return path_desc
                return "the " + path_desc

        world = self.world
        ent = world.node_to_desc_raw(id)
        if world.get_prop(id, "capitalize", False) is True:
            ent = ent.capitalize()
        if world.has_prop(id, "dead"):
            ent = "dead " + ent
        if world.has_prop(id, "player_name"):
            ent = world.get_prop(id, "player_name")
        elif world.has_prop(id, "agent") or world.has_prop(id, "object"):
            prefix = self.name_prefix_id(id, ent, use_the)
            if prefix != "" and not drop_prefix:
                # -- clean up data, TODO: shouldn't need this?
                if ent.lower().startswith("a "):
                    ent = ent[2:]
                if ent.lower().startswith("an "):
                    ent = ent[3:]
                if ent.lower().startswith("the "):
                    ent = ent[4:]
                # ---- end clean up --------------
                ent = prefix + " " + ent
        elif world.has_prop(id, "room"):
            prefix = self.name_prefix_id(id, ent, use_the)
            if prefix != "":
                ent = prefix + " " + ent
            else:
                ent = "the " + ent
        return ent

    def get_path_ex_desc(self, from_id, id, looker_id=None):
        """Return a path description. If both ids are the same return the
        room description instead.
        """
        world = self.world
        if from_id == id:
            if looker_id is not None:
                desc = world.get_prop(from_id, "desc")
                extra_desc = world.get_prop(from_id, "extra_desc")
                return extra_desc if extra_desc is not None else desc
            desc = world.get_prop(from_id, "desc")
            return world.get_prop(from_id, "extra_desc", desc)
        return world.oo_graph.get_edge(from_id, id).get_examine_desc()

    def path_to_desc(self, node, from_node):
        """get the description for a path from the perspective of from_node"""
        if node == from_node:
            return False
        edge = from_node.get_edge_to(node)
        if edge is not None:
            return f"{edge.label}"
        else:
            return False

    @deprecated
    def path_to_desc_id(self, id, from_id):
        """get the description for a path from the perspective of id2"""
        if id == from_id:
            return False
        if not isinstance(self.world.oo_graph.get_node(id), GraphRoom):
            return False
        if not isinstance(self.world.oo_graph.get_node(from_id), GraphRoom):
            return False
        edge = self.world.oo_graph.get_edge(from_id, id)
        if edge is not None:
            return f"{edge.label}"
        else:
            return False

    def name_prefix(self, node, txt, use_the):
        """Get the prefix to prepend an object with in text form"""
        # Get the preferred prefix type.
        pre = node.get_prop("name_prefix")
        if pre == "":
            return pre

        if use_the is True:
            return "the"

        if pre is False or pre is None or pre == "auto":
            txt = "an" if txt[0] in ["a", "e", "i", "o", "u"] else "a"
            return txt
        return pre

    @deprecated
    def name_prefix_id(self, id, txt, use_the):
        """Get the prefix to prepend an object with in text form"""
        # Get the preferred prefix type.
        pre = self.world.oo_graph.get_node(id).get_prop("name_prefix")
        if pre == "":
            return pre

        if use_the is True:
            return "the"

        if pre is False or pre is None or pre == "auto":
            txt = "an" if txt[0] in ["a", "e", "i", "o", "u"] else "a"
            return txt
        return pre

    def get_room_edge_text(self, room_descs):
        """Get text for all the edges outside of a room"""
        if len(room_descs) == 1:
            return f"There's {room_descs[0]}.\n"

        default_paths = [
            path[10:] for path in room_descs if path.startswith("a path to")
        ]
        non_default_paths = [
            path for path in room_descs if not path.startswith("a path to")
        ]
        if len(default_paths) == 0:
            return f"There's {self.display_desc_list(non_default_paths)}.\n"
        elif len(non_default_paths) == 0:
            return f"There are paths to {self.display_desc_list(default_paths)}.\n"
        else:
            non_default_path_text = ", ".join(non_default_paths)
            if len(default_paths) == 1:
                default_path_format = ", and a path to {}"
            else:
                default_path_format = ", and paths to {}"
            default_path_text = default_path_format.format(
                self.display_desc_list(default_paths)
            )
            return f"There's {non_default_path_text}{default_path_text}.\n"

    def get_room_object_text(self, object_descs, ents, give_empty=True):
        """Get text for all the objects in a room"""
        if len(object_descs) == 0:
            if not give_empty:
                return ""
            return "It is empty.\n"
        elif len(object_descs) > 20:
            return "There are a lot of things here.\n"
        else:
            return f"There's {self.display_desc_list(object_descs, ents)} here.\n"

    def get_room_agent_text(self, agent_descs):
        """Get text for all the agents in a room"""
        loc = "here"
        you_are = "You are "
        is_tensed = " is "
        are_tensed = " are "
        count = len(agent_descs)
        if count == 0:
            return ""
        elif count == 1:
            if agent_descs[0] == "you":
                return "You are here.\n"
            else:
                return f"{agent_descs[0].capitalize()} is here.\n"
        elif count == 2:
            all_descs = " and ".join(agent_descs).capitalize()
            return f"{all_descs} are here.\n"
        else:
            before_and = ", ".join(agent_descs[:-1]).capitalize()
            all_descs = f"{before_and}, and {agent_descs[-1]}"
            return f"{all_descs} are here.\n"

    def cnt_obj(self, obj, c, ents=None):
        """Return a text form of the count of an object"""
        world = self.world
        cnt = c[obj]
        if cnt == 1:
            return obj
        else:
            if ents is not None:
                if world.get_prop(ents[obj], "plural") is not None:
                    words = world.get_prop(ents[obj], "plural").split(" ")
                else:
                    if obj[-1] != "s":
                        words = (obj + "s").split(" ")
                    else:
                        words = (obj).split(" ")

            cnt = cnt - 2
            if cnt > 8:
                cnt = 8
            cnt = NUMS_ARRAY[cnt]
            if words[0] == "some":
                return " ".join(words)
            else:
                return cnt + " " + " ".join(words[1:])

    def display_desc_list(self, descs, ents=None):
        if len(descs) == 0:
            return "nothing"
        if len(descs) == 1:
            return descs[0]
        c = Counter(descs)
        unique_items = set(descs)
        s = ""
        cnt = 0
        for obj in unique_items:
            s += self.cnt_obj(obj, c, ents)
            if len(unique_items) > 2 and cnt < len(unique_items) - 1:
                s += ","
            s += " "
            cnt = cnt + 1
            if cnt == len(unique_items) - 1:
                s += "and "
        return s.rstrip(" ")

    @deprecated
    def display_node_list_id(self, l, from_id=False):
        desc_to_ent = {self.world.node_to_desc(ent, from_id): ent for ent in l}
        descs = [self.world.node_to_desc(ent, from_id) for ent in l]
        return self.display_desc_list(descs, desc_to_ent)

    def display_node_list(self, l, from_node=None):
        """Return the view for all the nodes in l as viewed from from_node"""
        desc_to_ent = {ent.get_view_from(from_node): ent for ent in l}
        descs = [ent.get_prefix_view_from(from_node) for ent in l]
        return self.display_desc_list(descs, desc_to_ent)

    def node_contents(self, node):
        """return a string for the contents within a node"""
        world = self.world
        if node.get_prop("surface_type") == "on":
            content_desc = self.display_node_list(node.get_contents())
            obj_desc = self.get_node_desc(node, use_the=True)
            return "There's {} on {}.".format(content_desc, obj_desc)
        else:
            s = self.get_node_desc(node, use_the=True).capitalize() + " contains "
            content_desc = self.display_node_list(node.get_contents())
            return s + content_desc + ".\n"

    def help_text(self):
        # scroll_line = "="*40 + '\n'
        scroll_line = ((emoji.emojize(":scroll:", use_aliases=True) + " ") * 20) + "\n"
        txt = (
            (
                "You pull some scribbled notes on a torn manuscript out of your pocket.\n"
                + "It reads:\n"
            )
            + scroll_line
            + ("Thine Commands:\n")
            + scroll_line
            + (
                "quest/goal/mission\n"
                "stats/status/health\n"
                "inventory (i or inv, for short)\n"
                'say/shout "<thing you want to say>; or use quotes only for short "\n'
                'tell/whisper <agent> "<something>"\n'
                "look (l, for short)\n"
                'go <direction>, e.g. "go north", or "go n" or just "n" for short\n'
                "examine <thing> (ex, for short)\n"
                "get/drop <object>\n"
                "eat/drink <object>\n"
                "wear/remove <object>\n"
                "wield/unwield <object>\n"
                "use <object> with <object>\n"
                "follow <agent>\n"
                "hit <agent>\n"
                "put <object> in <container>\n"
                "get <object> from <container>\n"
                "give <object> to <agent>\n"
                "point to <object>, e.g. good for trading\n"
                "steal <object> from <agent>\n"
                "emotes: laugh,cry,smile,ponder,blush,shrug,sigh,\n"
                "        wink,yawn,wave,stare,scream,pout,nudge,nod,\n"
                "        growl,groan,grin,gasp,frown,dance,applaud\n"
            )
            + scroll_line
        )
        # ((emoji.emojize(':scroll:', use_aliases=True) + ' ')*20) + '\n')
        return txt

    def get_vocab(self):
        """Return all the vocab this agent introduces into LIGHT"""
        return (
            [
                "a",
                "an",
                "and",
                "are",
                "carrying",
                "contains",
                "dead",
                "empty",
                "here",
                "is",
                "it",
                "lot",
                "nothing",
                "of",
                "on",
                "path",
                "paths",
                "some",
                "to",
                "the",
                "there",
                "there's",
                "things",
                "wearing",
                "wielding",
                "you",
            ]
            + ((" ".join(NUMS_ARRAY).strip()).split(" "))
            + (" ".join([h[0] for h in HEALTH_TUPLES]).split(" "))
        )
