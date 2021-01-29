import random
import json
from light.graph.elements.graph_nodes import (
    GraphAgent,
    GraphNode,
)
from light.graph.events.base import TriggeredEvent

magic_db = None


def init_magic(datapath):
    global magic_db
    if datapath is not None and len(datapath) > 0:
        with open(datapath, "r") as jsonfile:
            magic_db = json.load(jsonfile)
            print("[ loaded " + str(len(magic_db)) + " magic items]")


def mort(agent, event):
    pass


class CreationEvent(TriggeredEvent):
    def view_as(self, viewer: GraphAgent):
        """Provide the way that the given viewer should view this event"""
        if self.item is None:
            # Nothing happened.
            if viewer == self.actor:
                return "Nothing seems to happen."
            return

        text = (
            "Zap! A mighty roar sounds! Out of thin air, "
            + self.item.get_prefix_view()
            + " appears!"
        )
        if viewer == self.actor:
            return "You wave your hands around as you chant the words. " + text
        else:
            return text

    def to_canonical_form(self) -> str:
        """return action text for equipping the object"""
        # TODO: not sure how to do this.
        return "create TODO"


def find_item(txt):
    obs = []
    for i in range(0, len(magic_db)):
        if txt in magic_db[i]["name"]:
            obs.append(i)
    if len(obs) == 0:
        return {}
    else:
        obj = magic_db[random.choice(obs)]
        obj["is_object"] = True
        return obj


def creo(agent, event):
    # creation location
    room = event.actor.get_room()
    g = agent.world.oo_graph
    obj = find_item(event.text_content.replace("creo ", ""))
    new_event = CreationEvent(event.actor)
    new_event.actor = event.actor
    new_event.room = room
    new_event.item = None
    if obj.get("is_object", False):
        item = g.add_object(obj["name"], obj)
        if event.actor.would_fit(item) and item.size == 1:
            item.force_move_to(event.actor)
        else:
            item.force_move_to(room)
        new_event.item = item
    agent.world.broadcast_to_room(new_event)


def check_if_cast_magic_from_event(agent, event):
    event_name = event.__class__.__name__
    if event_name == "SayEvent":
        if event.text_content.startswith("creo "):
            creo(agent, event)
        if event.text_content.startswith("mort "):
            mort(agent, event)
