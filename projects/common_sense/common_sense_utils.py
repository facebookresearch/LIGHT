#!/usr/bin/env python3


# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import parlai.utils.logging as logging
from parlai.core.agents import Agent
import light.modeling.tasks.common_sense.constants as consts
from light.modeling.tasks.common_sense.agents import generate_graph_tuples
from parlai.core.agents import create_agent
import random


def verify_add_item_graph_tuple(graph_tuple, true_room_name, errors=None):
    """
    Verify a generated graph tuple has the correct form.

    Item add tuples should have structure new_name -=- IS_INSIDE -=- room_name
    """
    split_tuple = graph_tuple.split(consts.GRAPH_TUPLES_DELIM)
    if len(split_tuple) != 3:
        if errors is not None:
            errors.append(f"incorrect size: {len(split_tuple)} -=--=- 3")
        return False
    # confirmed the tuple has 3 parts, we don't care about the name but get the edge and room_name values
    _, edge, room_name = split_tuple
    # check correct edge
    if edge != consts.GraphEdges.IS_INSIDE.name:
        if errors is not None:
            errors.append(
                f"incorrect edge: {edge} -=--=- {consts.GraphEdges.IS_INSIDE.name}"
            )
        return False
    # check correct predicted name
    if room_name != true_room_name:
        if errors is not None:
            errors.append(f"incorrect room name: {room_name} -=--=- {true_room_name}")
        return False

    # passes all checks, is valid
    return True


def verify_add_room_attribute_graph_tuple(
    graph_tuple, true_room_name, true_graph_edge, errors=None
):
    """
    Verify a generated graph tuple has the correct form for room attributes Item add
    tuples should have structure room_name -=- edge_name -=- new_value.
    """
    split_tuple = graph_tuple.split(consts.GRAPH_TUPLES_DELIM)
    if len(split_tuple) != 3:
        if errors is not None:
            errors.append(f"incorrect size: {len(split_tuple)} -=--=- 3")
        return False
    # confirmed the tuple has 3 parts, we don't care about the value but get the name and edge
    room_name, edge, _ = split_tuple
    # check correct edge name
    if edge != true_graph_edge:
        if errors is not None:
            errors.append(f"incorrect edge: {edge} -=--=- {true_graph_edge}")
        return False
    # check correct room name
    if room_name != true_room_name:
        if errors is not None:
            errors.append(f"incorrect room name: {room_name} -=--=- {true_room_name}")
        return False

    # passes all checks, is valid
    return True


def verify_add_item_attribute_graph_tuple(
    graph_tuple, true_graph_edge, value_options=None, errors=None
):
    """
    Verify a generated graph tuple has the correct form for item attributes Item add
    tuples should have structure item_name -=- edge_name -=- new_value.

    value_options: list or None, if not None should be a list of valid strings the edge value can be
    """
    split_tuple = graph_tuple.split(consts.GRAPH_TUPLES_DELIM)
    if len(split_tuple) != 3:
        if errors is not None:
            errors.append(f"incorrect size: {len(split_tuple)} -=--=- 3")
        return False
    # confirmed the tuple has 3 parts, we don't care about the value or name but can verify the edge name
    _, edge, value = split_tuple
    # check correct edge name
    if edge != true_graph_edge:
        if errors is not None:
            errors.append(f"incorrect edge: {edge} -=--=- {true_graph_edge}")
        return False

    if value_options is not None:
        if value not in value_options:
            if errors is not None:
                errors.append(f"incorrect value: {value} not in {value_options}")
            return False

    # passes all checks, is valid
    return True


def verify_add_secondary_item(graph_tuple, graph_edge_name, errors=None):
    """
    Verify a generated graph tuple has the correct form.

    Item add tuples should have structure new_name -=- IS_INSIDE -=- room_name
    """
    split_tuple = graph_tuple.split(consts.GRAPH_TUPLES_DELIM)
    if len(split_tuple) != 3:
        if errors is not None:
            errors.append(f"incorrect size: {len(split_tuple)} -=--=- 3")
        return False
    # confirmed the tuple has 3 parts, we only check the edge type at this step
    _, edge, _ = split_tuple

    # check correct edge
    if edge != graph_edge_name:
        if errors is not None:
            errors.append(f"incorrect edge: {edge} -=--=- {graph_edge_name}")
        return False
    # passes all checks, is valid
    return True


def conditional_add_item_to_graph(
    existing_room_graph, graph_modification, item_type, errors=None
):
    """
    Add a new item (object or character) to the existing room graph, if it does not
    already exist.
    """
    # only modify graph if graph modification starts with add:
    if not graph_modification.startswith("ADD: "):
        logging.warning(
            f"Invalid graph modification '{graph_modification}' does not start with 'ADD: ', no item added."
        )
        if errors is not None:
            errors.append("start")

        return existing_room_graph

    graph_tuple = graph_modification.split("ADD: ")[1]
    room_name = existing_room_graph["setting"]
    if not verify_add_item_graph_tuple(graph_tuple, room_name, errors=errors):
        logging.warning(
            f"Invalid graph modification '{graph_modification}'. Expected 3 parts, {room_name}, and {consts.GraphEdges.IS_INSIDE.name} edge. No item added."
        )
        return existing_room_graph
    new_item_name = graph_tuple.split(consts.GRAPH_TUPLES_DELIM)[0]

    item_list = existing_room_graph[item_type]

    # NOTE: this new item may have the same name as another, they should receive unique ids
    item_list.append(
        {
            "name": new_item_name,
            "element_type": item_type,
            "is_in_room": True,
            "carrying_objects": [],
            "wearing_objects": [],
            "wielding_objects": [],
        }
    )
    if errors is not None:
        errors.append("correct")

    return existing_room_graph


def conditional_add_room_attribute_to_graph(
    existing_room_graph, graph_modification, edge_name, true_graph_edge, errors=None
):
    """
    Add a room attribute (e.g. backstory) to the existing room graph.
    """
    # only modify graph if graph modification starts with add:
    if not graph_modification.startswith("ADD: "):
        logging.warning(
            f"Invalid graph modification '{graph_modification}' does not start with 'ADD: ', no room attribute added."
        )
        if errors is not None:
            errors.append("start")
        return existing_room_graph

    graph_tuple = graph_modification.split("ADD: ")[1]

    room_name = existing_room_graph["setting"]
    if not verify_add_room_attribute_graph_tuple(
        graph_tuple, room_name, true_graph_edge, errors=errors
    ):
        logging.warning(
            f"Invalid graph tuple '{graph_tuple}'. Expected 3 parts: {room_name}, {true_graph_edge} and a value. No room attribute added."
        )
        return existing_room_graph

    edge_value = graph_tuple.split(consts.GRAPH_TUPLES_DELIM)[-1]
    existing_room_graph[edge_name] = edge_value
    errors.append("correct")
    return existing_room_graph


def find_item(existing_room_graph, target_id, item_type=None):
    """
    Find an item given a room graph, target id, and optional item type (item_type helps
    reduce search space)
    """
    search_secondary = item_type in (None, "objects")
    for primary_type in ["characters", "objects"]:
        if item_type == "characters" and primary_type != item_type:
            # "objects" includes secondary objects so we also need to search characters
            # if item type is "characters" we only need to search characters specifically
            # Regardless if the primary type is equal to the item type search this item list
            continue

        item_list = existing_room_graph[primary_type]
        for _, item in enumerate(item_list):
            if item.get("db_id", item["name"]) == target_id:
                return item

            # NOTE: to be changed once contained objects are complete dicts with attributes
            # currently only characters have secondary lists with dict items
            # only search if secondary objects are a possibility
            if primary_type == "characters" and search_secondary:
                for secondary_list in [
                    "carrying_objects",
                    "wearing_objects",
                    "wielding_objects",
                ]:
                    for _, secondary_item in enumerate(item.get(secondary_list, [])):
                        # NOTE: during testing items may not have db_ids but should always have names
                        # In deployment, items should always have both
                        if (
                            secondary_item.get("db_id", secondary_item["name"])
                            == target_id
                        ):
                            return secondary_item
    return None


def search_and_modify(
    existing_room_graph,
    edge_name,
    edge_value,
    target_id,
    predicted_name,
    item_type=None,
    errors=None,
):
    """
    Searches through all items for matching db_id and modifies accordingly Returns
    potentially modified graph and True if the graph was modified False if not.
    """
    item = find_item(existing_room_graph, target_id, item_type=item_type)
    if item is not None:
        if item.get("name", "") != predicted_name:
            # item found using target id doesn't have predicted name
            logging.warning(
                f"Target's name does not match predicted name in graph modification {predicted_name} vs {item.get('name', '')}, no change performed."
            )
            if errors is not None:
                errors.append(
                    f"incorrect name: {predicted_name} -=--=- {item.get('name', '')}"
                )
            return existing_room_graph, False

        item[edge_name] = edge_value
        return existing_room_graph, True
    else:
        logging.warning(
            f"Failed to find matching item for target {target_id}, no change performed."
        )
        if errors is not None:
            errors.append(f"no match: {target_id} not found")
    return existing_room_graph, False


def conditional_add_static_item_edge_to_graph(
    existing_room_graph, graph_modification, target_id, true_graph_edge, errors=None
):
    """
    Add an item attribute to the existing room graph, if the item already exists.
    """
    # only modify graph if graph modification starts with add:
    if not graph_modification.startswith("ADD: "):
        logging.warning(
            f"Invalid graph modification '{graph_modification}' does not start with 'ADD: ', no item edge added."
        )
        if errors is not None:
            errors.append("start")
        return existing_room_graph

    graph_tuple = graph_modification.split("ADD: ")[1]

    value_options = consts.ATTRIBUTE_VALUES[true_graph_edge]
    options_list = set([txt for values in value_options.values() for txt in values])

    if not verify_add_item_attribute_graph_tuple(
        graph_tuple, "HAS_ATTRIBUTE", value_options=options_list, errors=errors
    ):
        logging.warning(
            f"Invalid graph tuple '{graph_tuple}'. Expected 3 parts, HAS_ATTRIBUTE and a value in {options_list}. No item edge added."
        )
        return existing_room_graph

    graph_tuples = graph_tuple.split(consts.GRAPH_TUPLES_DELIM)
    # format is: name -=- has_attribute -=- value
    predicted_value = graph_tuples[-1]
    edge_value = 0
    # iterate over option: (option text 1, option text 2) pairs
    # due to validation we know that a match does exist
    for option, option_texts in value_options.items():
        if predicted_value in option_texts:
            edge_value = option
            break

    predicted_name = graph_tuples[0]
    edge_name = true_graph_edge.lower()
    existing_room_graph, modified = search_and_modify(
        existing_room_graph,
        edge_name,
        edge_value,
        target_id,
        predicted_name,
        item_type=None,
        errors=errors,
    )
    if modified:
        if errors is not None:
            errors.append("correct")
        return existing_room_graph

    return existing_room_graph


def conditional_add_item_edge_to_graph(
    existing_room_graph,
    graph_modification,
    target_id,
    edge_name,
    item_type,
    true_graph_edge,
    errors=None,
):
    """
    Add an item attribute to the existing room graph, if the item already exists.
    """
    # only modify graph if graph modification starts with add:
    if not graph_modification.startswith("ADD: "):
        logging.warning(
            f"Invalid graph modification '{graph_modification}' does not start with 'ADD: ', no item edge added."
        )
        if errors is not None:
            errors.append("start")
        return existing_room_graph

    graph_tuple = graph_modification.split("ADD: ")[1]

    if not verify_add_item_attribute_graph_tuple(
        graph_tuple, true_graph_edge, errors=errors
    ):
        logging.warning(
            f"Invalid graph tuple '{graph_tuple}'. Expected 3 parts and {true_graph_edge}. No item edge added."
        )
        return existing_room_graph

    edge_value = graph_tuple.split(consts.GRAPH_TUPLES_DELIM)[-1]
    graph_tuples = graph_tuple.split(consts.GRAPH_TUPLES_DELIM)
    # format is: name -=- edge_name -=- value
    edge_value = graph_tuples[-1]
    predicted_name = graph_tuples[0]

    existing_room_graph, modified = search_and_modify(
        existing_room_graph,
        edge_name,
        edge_value,
        target_id,
        predicted_name,
        item_type=item_type,
        errors=errors,
    )
    if modified:
        if errors is not None:
            errors.append("correct")
        return existing_room_graph

    return existing_room_graph


def conditional_add_secondary_item_to_graph(
    existing_room_graph,
    graph_modification,
    target_id,
    secondary_edge_name,
    item_type,
    graph_edge_name,
    errors=None,
):
    """
    Add a secondary item (e.g. object being worn) to the existing room graph, if the
    corresponding primary item already exists.
    """
    # only modify graph if graph modification starts with add:
    if not graph_modification.startswith("ADD: "):
        logging.warning(
            f"Invalid graph modification '{graph_modification}' does not start with 'ADD: ', no secondary item added."
        )
        if errors is not None:
            errors.append("start")
        return existing_room_graph

    graph_tuple = graph_modification.split("ADD: ")[1]

    if not verify_add_secondary_item(graph_tuple, graph_edge_name, errors=errors):
        logging.warning(
            f"Invalid graph tuple '{graph_tuple}'. Expected 3 parts and {graph_edge_name}. No secondary item added."
        )
        return existing_room_graph

    n1, _, n2 = graph_tuple.split(consts.GRAPH_TUPLES_DELIM)
    # depending on the type of edge secondary items can be constructed as secondary -=- edge -=- primary, or primary -=- edge -=- secondary
    secondary_item_name = n2
    primary_item_name = n1
    if graph_edge_name in consts.SECONDARY_FIRST_EDGES:
        secondary_item_name = n1
        primary_item_name = n2

    item = find_item(existing_room_graph, target_id, item_type=item_type)
    if item is not None:
        if item.get("name", "") != primary_item_name:
            # item found using target id doesn't have predicted name
            logging.warning(
                f"Target's name does not match predicted name in graph modification {primary_item_name} vs {item.get('name', '')}, no secondary item added."
            )
            if errors is not None:
                errors.append(
                    f"incorrect name: {primary_item_name} -=--=- {item.get('name', '')}"
                )
        else:
            # correct item found, success
            secondary_items = item.get(secondary_edge_name, [])
            if item_type == "characters":
                # currently character->secondary objects are dictionaries while object->secondary objects are not
                secondary_items.append({"name": secondary_item_name})
            elif item_type == "objects":
                secondary_items.append(secondary_item_name)
            if errors is not None:
                errors.append("correct")
    else:
        logging.warning(
            f"Failed to find matching item for target {target_id}, no secondary item added."
        )
        if errors is not None:
            errors.append(f"no match: {target_id} not found")
    return existing_room_graph


class CommonSenseAgent(Agent):
    """
    Agent with extra helper methods for World Builder API, used for constructing rooms.
    """

    def __init__(
        self,
        opt,
        model_name="bart_all_weighted_Wed_Nov_10/703",
        shared=None,
        force_add=True,
        verbose=False,
        count_errors=False,
        inference="beam",
        beam_size=2,
    ):
        opt[
            "model_file"
        ] = f"/checkpoint/alexgurung/light/common_sense/add_format/{model_name}/model"

        opt["single_turn"] = True
        opt["datatype"] = "test"
        if "override" not in opt:
            opt["override"] = {}

        opt["override"]["inference"] = inference
        opt["override"]["beam_size"] = beam_size
        self.force_add = force_add
        opt["override"]["opt_prefix_tokens"] = [29270, 29] if self.force_add else []
        self.opt = opt
        self.verbose = verbose
        self.count_errors = count_errors
        self.errors = [] if self.count_errors else None
        self.tasks = [] if self.count_errors else None
        self.graph_modifications = [] if self.count_errors else None
        self.internal_agent = create_agent(opt, requireModelExists=True)
        super().__init__(opt, shared)

    def get_errors(self):
        return self.errors

    def get_tasks(self):
        return self.tasks

    def get_graph_mods(self):
        return self.graph_modifications

    def clear_errors(self):
        self.errors = [] if self.count_errors else None
        self.tasks = [] if self.count_errors else None
        self.graph_modifications = [] if self.count_errors else None

    def observe(self, observation):
        return self.internal_agent.observe(observation)

    def act(self):
        return self.internal_agent.act()

    def parse_room_graph(self, graph_object):
        """
        Helper method, returns the graph object formatted in graph tuples as interpreted
        by the model.
        """
        element_types = [
            consts.ElementType.ROOM,
            consts.ElementType.OBJECT,
            consts.ElementType.CHARACTER,
        ]
        return generate_graph_tuples(
            graph_object,
            element_types,
            only_in_edges=True,
            dropouts={},
            label_tuples=set(),
            remove_reference=False,
        )

    def generate_from_graph(self, existing_room_graph, prompt):
        """
        Helper method to handle calling the model (internal_agent) on the given prompt
        and room graph.
        """
        context = self.parse_room_graph(existing_room_graph)
        input_text = context + "\n" + prompt

        self.observe({"text": input_text, "sender": "human", "episode_done": True})
        act = self.act()
        if self.verbose:
            logging.info(f"Prompt: {prompt}")
            logging.info(f"Output: {act['text']}")

        if self.graph_modifications is not None:
            self.graph_modifications.append(act["text"])
        return act["text"]

    def add_room_description(self, existing_room_graph):
        """
        Predicts a room description graph tuple and attempts to add it to the graph,
        returns modified room graph.
        """
        if self.tasks is not None:
            self.tasks.append("room_description")
        prompt = random.choice(consts.TEACHER_PROMPTS["room_description"])
        old_inference = self.internal_agent.opt["inference"]
        self.internal_agent.opt["inference"] = "nucleus"
        graph_modification = self.generate_from_graph(existing_room_graph, prompt)
        self.internal_agent.opt["inference"] = old_inference
        existing_room_graph = conditional_add_room_attribute_to_graph(
            existing_room_graph,
            graph_modification,
            "description",
            consts.GraphEdges.HAS_DESCRIPTION.name,
            errors=self.errors,
        )

        return existing_room_graph

    def add_room_backstory(self, existing_room_graph):
        """
        Predicts a room backstory graph tuple and attempts to add it to the graph,
        returns modified room graph.
        """
        if self.tasks is not None:
            self.tasks.append("room_backstory")
        prompt = random.choice(consts.TEACHER_PROMPTS["room_backstory"])
        old_inference = self.internal_agent.opt["inference"]
        self.internal_agent.opt["inference"] = "nucleus"
        graph_modification = self.generate_from_graph(existing_room_graph, prompt)
        self.internal_agent.opt["inference"] = old_inference
        existing_room_graph = conditional_add_room_attribute_to_graph(
            existing_room_graph,
            graph_modification,
            "background",
            consts.GraphEdges.HAS_BACKSTORY.name,
            errors=self.errors,
        )

        return existing_room_graph

    def handle_generation_opts(
        self, existing_room_graph, count=0, item_type="characters"
    ):
        """
        Helper method to modify the commonsense model's hyper-parameters for forcing
        generation.

        NOTE: these hyper-parameters are only useful with the corresponding parlai agent and beam search changes
        """
        # removed temporarily until unique beam blocking functional
        pass

    def id_to_name(self, existing_room_graph, target_id, item_type=None):
        """
        Helper method to get the name of an item from the node id.

        If item_type is provided, search specific item type, otherwise search all items

        If a node with the id doesn't exist, return id
        """
        item = find_item(existing_room_graph, target_id, item_type=None)
        if item is not None:
            return item["name"]

        # no item with matching id found, returning id
        return target_id

    def add_object(self, existing_room_graph, count=0):
        """
        Predicts 'count' new object graph tuples and attempts to add them to the graph,
        returns modified room graph.
        """
        iterations = max(count, 1)
        for _ in range(iterations):
            if self.tasks is not None:
                self.tasks.append("add_object")
            self.handle_generation_opts(
                existing_room_graph, count=count, item_type="objects"
            )
            prompt = random.choice(consts.TEACHER_PROMPTS["adding_objects"])
            graph_modification = self.generate_from_graph(existing_room_graph, prompt)
            existing_room_graph = conditional_add_item_to_graph(
                existing_room_graph, graph_modification, "objects", errors=self.errors
            )

        return existing_room_graph

    def add_character(self, existing_room_graph, count=0):
        """
        Predicts 'count' new character graph tuples and attempts to add them to the
        graph, returns modified room graph.
        """
        iterations = max(count, 1)
        for _ in range(iterations):
            if self.tasks is not None:
                self.tasks.append("add_character")
            self.handle_generation_opts(
                existing_room_graph, count=count, item_type="characters"
            )
            prompt = random.choice(consts.TEACHER_PROMPTS["adding_characters"])
            graph_modification = self.generate_from_graph(existing_room_graph, prompt)
            existing_room_graph = conditional_add_item_to_graph(
                existing_room_graph,
                graph_modification,
                "characters",
                errors=self.errors,
            )

        return existing_room_graph

    def generic_add_secondary_object(
        self,
        existing_room_graph,
        target_id,
        prompt_name,
        edge_name,
        graph_edge_name,
        item_type,
        count=0,
    ):
        """
        Predicts 'count' new secondary object graph tuples and attempts to add them to
        the graph, returns modified room graph.

        Secondary objects are in reference to a target (e.g. a character), and a prompt
        (e.g. what does x wear)
        """
        iterations = max(count, 1)
        for _ in range(iterations):
            # generation opts use "objects" item type because we don't want to generate duplicate objects
            self.handle_generation_opts(
                existing_room_graph, count=count, item_type="objects"
            )
            # target name is found using item_type, in case we're referencing a character or object's secondary items
            target_name = self.id_to_name(
                existing_room_graph, target_id, item_type=item_type
            )
            prompt = random.choice(consts.TEACHER_PROMPTS[prompt_name]).format(
                name=target_name
            )
            graph_modification = self.generate_from_graph(existing_room_graph, prompt)

            existing_room_graph = conditional_add_secondary_item_to_graph(
                existing_room_graph,
                graph_modification,
                target_id,
                edge_name,
                item_type,
                graph_edge_name,
                errors=self.errors,
            )

        return existing_room_graph

    def add_object_contains(self, existing_room_graph, target_id, count=0):
        """
        Predicts 'count' new object graph tuples contained by target and attempts to add
        them to the graph, returns modified room graph.
        """
        if self.tasks is not None:
            for _ in range(max(count, 1)):
                self.tasks.append("object_contains")
        return self.generic_add_secondary_object(
            existing_room_graph,
            target_id,
            "adding_object_contains",
            "containing_objects",
            consts.GraphEdges.CONTAINS.name,
            # consts.GraphEdges.IS_INSIDE.name,
            "objects",
            count=count,
        )

    def add_character_wearing(self, existing_room_graph, target_id, count=0):
        """
        Predicts 'count' new object graph tuples worn by target and attempts to add them
        to the graph, returns modified room graph.
        """
        if self.tasks is not None:
            for _ in range(max(count, 1)):
                self.tasks.append("character_wearing")
        return self.generic_add_secondary_object(
            existing_room_graph,
            target_id,
            "adding_character_wearing",
            "wearing_objects",
            consts.GraphEdges.IS_WEARING.name,
            "characters",
            count=count,
        )

    def add_character_carrying(self, existing_room_graph, target_id, count=0):
        """
        Predicts 'count' new object graph tuples carried by target and attempts to add
        them to the graph, returns modified room graph.
        """
        if self.tasks is not None:
            for _ in range(max(count, 1)):
                self.tasks.append("character_carrying")
        return self.generic_add_secondary_object(
            existing_room_graph,
            target_id,
            "adding_character_carrying",
            "carrying_objects",
            consts.GraphEdges.IS_CARRYING.name,
            "characters",
            count=count,
        )

    def add_character_wielding(self, existing_room_graph, target_id, count=0):
        """
        Predicts 'count' new object graph tuples wielded by target and attempts to add
        them to the graph, returns modified room graph.
        """
        if self.tasks is not None:
            for _ in range(max(count, 1)):
                self.tasks.append("character_wielding")
        return self.generic_add_secondary_object(
            existing_room_graph,
            target_id,
            "adding_character_wielding",
            "wielding_objects",
            consts.GraphEdges.IS_WIELDING.name,
            "characters",
            count=count,
        )

    def generic_add_text_item_attribute(
        self,
        existing_room_graph,
        target_id,
        prompt_name,
        edge_name,
        item_type,
        true_graph_edge,
    ):
        """
        Runs generate and conditional add for adding an attribute to an item, e.g.
        physical description of an object.

        prompt_name: key for teacher prompts relating to this attribute (e.g. "adding_physical_description")
        edge_name: name this attribute has in the room graph (e.g. description)
        item_type: type of item, used for adding the generated modification the room graph (e.g. objects)
        """
        target_name = self.id_to_name(
            existing_room_graph, target_id, item_type=item_type
        )
        prompt = random.choice(consts.TEACHER_PROMPTS[prompt_name]).format(
            name=target_name
        )
        # for text generation specifically we want nucleus sampling to improve generation quality
        old_inference = self.internal_agent.opt["inference"]
        self.internal_agent.opt["inference"] = "nucleus"
        graph_modification = self.generate_from_graph(existing_room_graph, prompt)
        self.internal_agent.opt["inference"] = old_inference
        existing_room_graph = conditional_add_item_edge_to_graph(
            existing_room_graph,
            graph_modification,
            target_id,
            edge_name,
            item_type,
            true_graph_edge,
            errors=self.errors,
        )

        return existing_room_graph

    def add_object_description(self, existing_room_graph, target_id):
        """
        Predicts new object description graph tuple and attempts to add it to the graph,
        returns modified room graph.
        """
        if self.tasks is not None:
            self.tasks.append("object_description")
        return self.generic_add_text_item_attribute(
            existing_room_graph,
            target_id,
            "adding_physical_description",
            "description",
            "objects",
            consts.GraphEdges.HAS_DESCRIPTION.name,
        )

    def add_character_description(self, existing_room_graph, target_id):
        """
        Predicts new character description graph tuple and attempts to add it to the
        graph, returns modified room graph.
        """
        if self.tasks is not None:
            self.tasks.append("character_description")
        return self.generic_add_text_item_attribute(
            existing_room_graph,
            target_id,
            "adding_physical_description",
            "desc",
            "characters",
            consts.GraphEdges.HAS_DESCRIPTION.name,
        )

    def add_character_persona(self, existing_room_graph, target_id):
        """
        Predicts new character persona graph tuple and attempts to add it to the graph,
        returns modified room graph.
        """
        if self.tasks is not None:
            self.tasks.append("character_persona")
        return self.generic_add_text_item_attribute(
            existing_room_graph,
            target_id,
            "adding_character_persona",
            "persona",
            "characters",
            consts.GraphEdges.HAS_PERSONA.name,
        )

    def generic_add_static_item_attribute(
        self,
        existing_room_graph,
        target_id,
        prompt_name,
        true_graph_edge,
    ):
        """
        Runs generate and conditional add for adding a static attribute to an item, e.g.
        object is edible or surface.

        prompt_name: key for teacher prompts relating to this attribute (e.g. "adding_physical_description")
        true_graph_edge: name this attribute has in consts.ATTRIBUTE_VALUES (which in lowercase corresponds to db)
        """
        target_name = self.id_to_name(existing_room_graph, target_id, item_type=None)

        prompt = random.choice(consts.TEACHER_PROMPTS[prompt_name]).format(
            name=target_name
        )
        graph_modification = self.generate_from_graph(existing_room_graph, prompt)

        existing_room_graph = conditional_add_static_item_edge_to_graph(
            existing_room_graph,
            graph_modification,
            target_id,
            true_graph_edge,
            errors=self.errors,
        )

        return existing_room_graph

    def add_item_gettable(self, existing_room_graph, target_id):
        """
        Predicts whether item is gettable and adds the modification to the graph,
        returns modified room graph.
        """
        if self.tasks is not None:
            self.tasks.append("item_gettable")
        return self.generic_add_static_item_attribute(
            existing_room_graph, target_id, "attribute_qa_gettable", "IS_GETTABLE"
        )

    def add_item_drink(self, existing_room_graph, target_id):
        """
        Predicts whether item is drink and adds the modification to the graph, returns
        modified room graph.
        """
        if self.tasks is not None:
            self.tasks.append("item_drink")
        return self.generic_add_static_item_attribute(
            existing_room_graph, target_id, "attribute_qa_drink", "IS_DRINK"
        )

    def add_item_food(self, existing_room_graph, target_id):
        """
        Predicts whether item is food and adds the modification to the graph, returns
        modified room graph.
        """
        if self.tasks is not None:
            self.tasks.append("item_food")
        return self.generic_add_static_item_attribute(
            existing_room_graph, target_id, "attribute_qa_food", "IS_FOOD"
        )

    def add_item_container(self, existing_room_graph, target_id):
        """
        Predicts whether item is container and adds the modification to the graph,
        returns modified room graph.
        """
        if self.tasks is not None:
            self.tasks.append("item_container")
        return self.generic_add_static_item_attribute(
            existing_room_graph, target_id, "attribute_qa_container", "IS_CONTAINER"
        )

    def add_item_surface(self, existing_room_graph, target_id):
        """
        Predicts whether item is surface and adds the modification to the graph, returns
        modified room graph.
        """
        if self.tasks is not None:
            self.tasks.append("item_surface")
        return self.generic_add_static_item_attribute(
            existing_room_graph, target_id, "attribute_qa_surface", "IS_SURFACE"
        )

    def add_item_weapon(self, existing_room_graph, target_id):
        """
        Predicts whether item is weapon and adds the modification to the graph, returns
        modified room graph.
        """
        if self.tasks is not None:
            self.tasks.append("item_weapon")
        return self.generic_add_static_item_attribute(
            existing_room_graph, target_id, "attribute_qa_weapon", "IS_WIELDABLE"
        )

    def add_item_wearable(self, existing_room_graph, target_id):
        """
        Predicts whether item is wearable and adds the modification to the graph,
        returns modified room graph.
        """
        if self.tasks is not None:
            self.tasks.append("item_wearable")
        return self.generic_add_static_item_attribute(
            existing_room_graph, target_id, "attribute_qa_wearable", "IS_WEARABLE"
        )

    ##################################################################
    # Consolidation methods
    ##################################################################

    def add_all_static_attributes(self, existing_room_graph, target_id):
        """
        Fills in all static attributes for an item given its target id.
        """
        existing_room_graph = self.add_item_gettable(existing_room_graph, target_id)
        existing_room_graph = self.add_item_drink(existing_room_graph, target_id)
        existing_room_graph = self.add_item_food(existing_room_graph, target_id)
        existing_room_graph = self.add_item_container(existing_room_graph, target_id)
        existing_room_graph = self.add_item_surface(existing_room_graph, target_id)
        existing_room_graph = self.add_item_weapon(existing_room_graph, target_id)
        existing_room_graph = self.add_item_wearable(existing_room_graph, target_id)
        return existing_room_graph

    def add_all_object_attributes(self, existing_room_graph, target_id, count=0):
        """
        Fills in object given a target id and count for secondary objects.
        """
        existing_room_graph = self.add_object_description(
            existing_room_graph, target_id
        )
        existing_room_graph = self.add_object_contains(
            existing_room_graph, target_id, count=count
        )
        existing_room_graph = self.add_all_static_attributes(
            existing_room_graph, target_id
        )

        return existing_room_graph

    def add_all_character_attributes(self, existing_room_graph, target_id, count=0):
        """
        Fills in character given a target id and count for secondary objects.
        """
        existing_room_graph = self.add_character_description(
            existing_room_graph, target_id
        )
        existing_room_graph = self.add_character_persona(existing_room_graph, target_id)
        existing_room_graph = self.add_character_carrying(
            existing_room_graph, target_id, count=count
        )
        existing_room_graph = self.add_character_wearing(
            existing_room_graph, target_id, count=count
        )
        existing_room_graph = self.add_character_wielding(
            existing_room_graph, target_id, count=count
        )
        # now all secondary objects are added, fill in those objects
        # NOTE: if contained objects get more complex this could result in a recursive loop
        character = find_item(existing_room_graph, target_id, item_type="characters")
        for secondary_list in [
            "carrying_objects",
            "wearing_objects",
            "wielding_objects",
        ]:
            for _, secondary_item in enumerate(character.get(secondary_list, [])):
                secondary_id = secondary_item.get("db_id", secondary_item["name"])
                self.add_all_object_attributes(existing_room_graph, secondary_id)

        return existing_room_graph
