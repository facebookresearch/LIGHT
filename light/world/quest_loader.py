import os
import json
import random


class QuestLoader:
    """
    Loads quests from a directory, then lets them be queried
    randomly

    TODO query by character or other attributes
    """

    def __init__(self, quest_dir):
        self.quests = []
        for quest_file in os.listdir(quest_dir):
            if not quest_file.endswith(".json"):
                continue
            with open(os.path.join(quest_dir, quest_file), "r") as jsonfile:
                self.quests.append(json.load(jsonfile)["data"])

    def get_random_quest(self):
        """
        Get any random quest from the list of quests.
        """
        return random.choice(self.quests)


class QuestCreator:
    def __init__(self, opt):
        pass

    templates = {
        "obtain": [
            "I want OBJECT.",
            "I need OBJECT.",
            "I'm looking for OBJECT.",
            "I'd really like OBJECT.",
            "I must get OBJECT, urgently.",
        ],
        "give": [
            "I need to get OBJECT to AGENT.",
            "I want to give OBJECT to AGENT.",
            "I must get OBJECT to AGENT as soon as possible.",
            "I really need to give OBJECT to AGENT.",
        ],
        "drop": [
            "I need OBJECT in LOCATION as soon as possible.",
            "I'd like to get OBJECT in LOCATION.",
        ],
        "hug": ["I need a hug from AGENT.", "I want AGENT to show they care for me."],
        "laugh": ["I'd like to make AGENT laugh."],
        "converse": ["I'd like to converse with AGENT."],
        "smile": ["I'd like to make AGENT smile."],
        "hit": [
            "I want to make AGENT pay for what they've done.",
            "I want to get my revenge on AGENT.",
        ],
        "steal": [
            "I'd like to get OBJECT from AGENT.",
            "AGENT has OBJECT, and I want it.",
        ],
        "put": [
            "I need to put OBJECT IN CONTAINER.",
            "I want to get OBJECT IN CONTAINER.",
        ],
    }

    actions = {
        "obtain": "get OBJECT",
        "give": "give OBJECT to AGENT",
        "drop": "drop OBJECT in LOCATION",
        "hug": "hug AGENT",
        "laugh": "AGENT laughs",
        "converse": "talk to AGENT",
        "smile": "AGENT smiles",
        "hit": "hit AGENT",
        "steal": "steal OBJECT from AGENT",
        "put": "put OBJECT IN CONTAINER",
    }

    def pick_location(actor, graph, verb, arg, obj=None):
        # TODO: we could update this later to select from the set of objects
        # satisfying the constraints to be the one that best matches the agent,
        # e.g. using a starspace model.

        locs = list(graph.rooms)
        for i in range(0, 100):
            loc = random.choice(locs)
            loc = graph.rooms[loc]
            viable_target = True
            if (
                loc is not None
                and loc.container_node.get() == actor.container_node.get()
            ):
                viable_target = False
            if viable_target:
                return loc
        # Failed.
        return None

    def pick_agent(actor, graph, verb, arg, obj=None):
        # TODO: we could update this later to select from the set of objects
        # satisfying the constraints to be the one that best matches the agent,
        # e.g. using a starspace model.

        if verb == "steal":
            return obj.container_node.get()

        pers = list(graph.agents)
        for i in range(0, 100):
            per = random.choice(pers)
            per = graph.agents[per]
            viable_target = True
            # needs to not be actor themself
            if actor == per:
                viable_target = False
            if not per.agent:
                viable_target = False
            if viable_target:
                return per
        # Failed.
        return None

    def pick_object(actor, graph, verb, arg, other_obj=None):
        # TODO: we could update this later to select from the set of objects
        # satisfying the constraints to be the one that best matches the agent,
        # e.g. using a starspace model.
        objs = list(graph.objects)
        for i in range(0, 100):
            obj = random.choice(objs)
            obj = graph.objects[obj]
            viable_target = True
            # needs to be gettable unless it's a container
            if arg != "CONTAINER" and not obj.gettable:
                viable_target = False
            if verb == "obtain" or verb == "steal":
                # Should not be owned by actor
                if obj.container_node.get() == actor:
                    viable_target = False
            if verb == "steal":
                # Should be owned by another actor
                if obj.container_node.get() == actor:
                    viable_target = False
                if not obj.container_node.get().agent:
                    viable_target = False
            if arg == "CONTAINER":
                if obj == other_obj:
                    viable_target = False
                if not obj.container:
                    viable_target = False
                if obj.contain_size < other_obj.size:
                    viable_target = False

            if viable_target:
                return obj
        # Failed.
        return None

    def create_quest(actor, graph):
        for i in range(0, 20):
            quest = QuestCreator.create_random_quest(actor, graph)
            if quest is not None:
                break
        if quest is None:
            return None
        # Add quest to actor's list of quests.
        if actor.quests is None:
            actor.quests = []
        actor.quests.append(quest)
        return quest

    def create_random_quest(actor, graph):
        q_verb = random.choice(list(QuestCreator.templates.keys()))
        q_verb = "put"
        q_txt = random.choice(QuestCreator.templates[q_verb])
        obj = None
        loc = None
        per = None
        container = None
        if "OBJECT" in q_txt:
            obj = QuestCreator.pick_object(actor, graph, q_verb, "OBJECT")
            if obj is None:
                return  # failed to create quest right now (should be very rare).
            obj_txt = obj.get_prefix_view()
            q_txt = q_txt.replace("OBJECT", obj_txt)
        if "CONTAINER" in q_txt:
            container = QuestCreator.pick_object(actor, graph, q_verb, "CONTAINER", obj)
            if container is None:
                return  # failed to create quest right now (should be very rare).
            container_txt = container.get_prefix_view()
            q_txt = q_txt.replace("CONTAINER", container_txt)
            q_txt = q_txt.replace("IN", container.surface_type)
        if "AGENT" in q_txt:
            per = QuestCreator.pick_agent(actor, graph, q_verb, "AGENT", obj)
            if per is None:
                return  # failed to create quest right now (should be very rare).
            per_txt = per.get_prefix_view()
            q_txt = q_txt.replace("AGENT", per_txt)
        if "LOCATION" in q_txt:
            loc = QuestCreator.pick_location(actor, graph, q_verb, "LOCATION", obj)
            if loc is None:
                return  # failed to create quest right now (should be very rare).
            loc_txt = loc.get_prefix_view()
            q_txt = q_txt.replace("LOCATION", loc_txt)

        quest = {
            "text": q_txt,
            "goal_verb": q_verb,
            "object": obj.node_id if obj is not None else None,
            "container": container.node_id if container is not None else None,
            "location": loc.node_id if loc is not None else None,
            "actor": actor.node_id if actor is not None else None,
            "agent": per,
        }
        return quest
