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
            "I want to put OBJECT IN CONTAINER.",
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
        # TODO: we could update this later to select from the set of agents
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

    def pick_object(actor, graph, verb, arg, other_obj=None, new_loc=None):
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
            if verb == "drop":
                # Should not be already there.
                if obj.container_node.get() == new_loc:
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
                if other_obj.container_node.get() == obj:
                    # Goal already achieved.
                    viable_target = False

            if viable_target:
                return obj
        # Failed.
        return None

    def create_quest(actor, graph):
        if actor.quests is None or len(actor.quests) == 0:
            actor.quests = []
        else:
            # Already has a quest.
            return

        for i in range(0, 20):
            quest = QuestCreator.create_random_quest(actor, graph)
            if quest is not None:
                break
        if quest is None:
            return None
        # Add quest to actor's list of quests.
        actor.quests.append(quest)
        return quest

    def create_random_quest(actor, graph):
        q_verb = random.choice(list(QuestCreator.templates.keys()))
        # q_verb = "smile"
        q_txt = random.choice(QuestCreator.templates[q_verb])
        obj = None
        loc = None
        per = None
        container = None
        if "OBJECT" in q_txt:
            obj = QuestCreator.pick_object(actor, graph, q_verb, "OBJECT", new_loc=loc)
            if obj is None:
                return  # failed to create quest right now (should be very rare).
            obj_txt = obj.get_prefix_view()
            q_txt = q_txt.replace("OBJECT", obj_txt)
        if "CONTAINER" in q_txt:
            container = QuestCreator.pick_object(
                actor, graph, q_verb, "CONTAINER", other_obj=obj
            )
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
            "agent": per.node_id if per is not None else None,
            "helper_agents": [],  # Who has been told about this quest
        }
        return quest

    def event_involves(event, node_id):
        if event.actor.node_id == node_id:
            return True
        for n_id in event.target_nodes:
            if n_id.node_id == node_id:
                return True
        return False

    def contains(container_id, node_id, world):
        cid = world.oo_graph.all_nodes[node_id].container_node.get().node_id
        if cid == container_id:
            return True
        else:
            return False

    def same_room(node1_id, node2_id, world):
        r1 = world.oo_graph.all_nodes[node1_id].get_room()
        r2 = world.oo_graph.all_nodes[node2_id].get_room()
        if r1 == r2:
            return True
        else:
            return False

    def conversation_score_above_threshold(actor, agent, world):
        score = 3
        if score > 2:
            return True
        else:
            return False

    def quest_complete(world, actor, quest, event=None):
        text = "Quest Complete: " + quest["text"].rstrip(".").rstrip("!") + "!"
        # Assign XP.
        if not hasattr(actor, "xp"):
            actor.xp = 0
        xp = quest.get("goal_xp", 2)
        world.send_msg(actor, text + "\nYou gained " + str(xp) + " experience points.")
        actor.xp += xp
        # Find if someone helped complete the quest.
        helper_agents = quest["helper_agents"]
        if event is not None:
            for helper_agent in helper_agents:
                if event.actor == helper_agent:
                    # Reward that actor.
                    agent_str = actor.get_prefix_view()
                    world.send_msg(
                        helper_agent,
                        "You gained "
                        + str(xp)
                        + " experience points for helping "
                        + agent_str
                        + "!",
                    )

    def quest_matches_event(world, quest, event):
        #        import pdb; pdb.set_trace()
        qc = QuestCreator
        event_name = event.__class__.__name__

        if quest["goal_verb"] == "obtain":
            if (
                qc.event_involves(event, quest["actor"])
                and qc.event_involves(event, quest["object"])
                and qc.contains(quest["actor"], quest["object"], world)
            ):
                return True

        if quest["goal_verb"] == "give":
            if (
                qc.event_involves(event, quest["actor"])
                and qc.event_involves(event, quest["agent"])
                and qc.event_involves(event, quest["object"])
                and qc.contains(quest["agent"], quest["object"], world)
            ):
                return True

        if quest["goal_verb"] == "drop":
            if (
                qc.event_involves(event, quest["actor"])
                and qc.event_involves(event, quest["object"])
                and qc.contains(quest["location"], quest["object"], world)
            ):
                return True

        if quest["goal_verb"] == "hug":
            if (
                event_name == "HugEvent"
                and qc.event_involves(event, quest["actor"])
                and qc.event_involves(event, quest["agent"])
            ):
                return True

        if quest["goal_verb"] == "converse":
            if (
                (
                    event_name == "SayEvent"
                    or event_name == "TellEvent"
                    or event_name == "WhisperEvent"
                    or event_name == "ShoutEvent"
                )
                and qc.event_involves(event, quest["actor"])
                and qc.same_room(quest["actor"], quest["agent"], world)
                and qc.conversation_score_above_threshold(
                    quest["actor"], quest["agent"], world
                )
            ):
                return True

        if quest["goal_verb"] == "laugh":
            if (
                event_name == "EmoteEvent"
                and event.text_content == "laugh"
                and qc.event_involves(event, quest["agent"])
                and qc.same_room(quest["actor"], quest["agent"], world)
            ):
                return True

        if quest["goal_verb"] == "smile":
            if (
                event_name == "EmoteEvent"
                and event.text_content == "smile"
                and qc.event_involves(event, quest["agent"])
                and qc.same_room(quest["actor"], quest["agent"], world)
            ):
                return True

        if quest["goal_verb"] == "put":
            if (
                qc.event_involves(event, quest["actor"])
                and qc.event_involves(event, quest["object"])
                and qc.contains(quest["container"], quest["object"], world)
            ):
                return True

        if quest["goal_verb"] == "steal":
            if (
                qc.event_involves(event, quest["actor"])
                and qc.event_involves(event, quest["object"])
                and qc.contains(quest["actor"], quest["object"], world)
            ):
                return True

        if quest["goal_verb"] == "hit":
            if (
                event_name == "HitEvent"
                and quest["actor"] == event.actor.node_id
                and event.target_nodes[0].node_id == quest["agent"]
            ):
                return True

        return False
