#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import hashlib

from mephisto.operations.operator import Operator
from mephisto.tools.scripts import (
    build_custom_bundle,
    task_script,
)
from mephisto.operations.hydra_config import build_default_task_config
from mephisto.abstractions.blueprints.remote_procedure.remote_procedure_blueprint import (
    SharedRemoteProcedureTaskState,
    RemoteProcedureAgentState,
)
from common_sense_agent_utils import CommonSenseAgent
import json
from graph_converter_utils import (add_object_to_graph, 
                                    add_object_secondary_objects_to_graph,
                                    add_character_to_graph, 
                                    add_character_secondary_objects_to_graph,
                                    get_room_content_from_json, 
                                    replace_binarized_attributes_with_description, 
                                    run_create_char, 
                                    run_create_obj, 
                                    modify_room_attrs)

from omegaconf import DictConfig, MISSING
from typing import List, Any, Dict
from dataclasses import dataclass, field

from light.data_model.light_database import LIGHTDatabase
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from build_room_data import ROOM_ID_TO_ITEMS
import numpy as np
from config import LIGHT_DB_PATH

MAX_INCORRECT = 3

##############################
# TODO: add suggestion id
############### ###############

def get_salted_hash(in_string, salt):
    """Return a hash string for the given string using sha-256"""
    salted_string = in_string + salt + in_string
    res = hashlib.sha256(salted_string.encode("utf-8")).hexdigest()[:20]
    return res


@dataclass
class BuilderTaskConfig(build_default_task_config("local")):  # type: ignore
    game_url: str = field(
        default=MISSING,
        metadata={"help": "Complete URL to use for the version of the game running"},
    )


def validate_unit(unit):
    agent = unit.get_assigned_agent()
    if agent is None:
        return

    data = agent.state.get_data()

    if data["final_submission"] is None:
        return

    final_data = data["final_submission"]["data"]

    # TODO validate
    return


@task_script(config=BuilderTaskConfig)
def main(operator: Operator, cfg: DictConfig) -> None:
    tasks: List[Dict[str, Any]] = [{"url": cfg.game_url}] * cfg.num_tasks

    def validate_onboarding(onboarding_data):
        # TODO implement once we have an onboarding
        return True

    USE_MODEL = False
    # USE_MODEL = True
    MODEL_NAME = "bart_all_simple_Sun_Jan_23/c9d"
    world_builder_agent = None
    force = False
    opt_file = f"/checkpoint/alexgurung/light/common_sense/add_format/{MODEL_NAME}/model.opt"
    if os.path.exists(opt_file):
        with open(opt_file) as f:
            opt = json.load(f)

        if "override" not in opt:
            opt['override'] = {}
        opt['override']['skip_generation'] = False
        
        # TODO initialize agent as necessary for the below
        world_builder_agent = CommonSenseAgent(
            opt, model_name=MODEL_NAME, force_add=force, verbose=False, count_errors=True
            )

    db = None
    obj_vectorizer, obj_vectors, all_objects = None, None, None
    char_vectorizer, char_vectors, all_chars = None, None, None
    room_vectorizer, room_vectors, all_rooms = None, None, None
    if os.path.exists(LIGHT_DB_PATH):
        db = LIGHTDatabase(LIGHT_DB_PATH)
        with db as ldb:
            all_objects = [dict(obj) for obj in ldb.get_object()]

        with db as ldb:
            all_chars = [dict(obj) for obj in ldb.get_character()]

        with db as ldb:
            all_rooms = [dict(obj) for obj in ldb.get_room()]

        room_vectorizer = TfidfVectorizer(stop_words="english")
        room_texts = [room["name"] + "\n" + room['description'] for room in all_rooms]
        room_vectors = room_vectorizer.fit_transform(room_texts)

        obj_vectorizer = TfidfVectorizer(stop_words="english")
        obj_texts = [obj["name"] + "\n" + obj['physical_description'] for obj in all_objects]
        obj_vectors = obj_vectorizer.fit_transform(obj_texts)

        char_vectorizer = TfidfVectorizer(stop_words="english")
        char_texts = [char["name"] + "\n" + char['physical_description'] + "\n" + char["persona"] for char in all_chars]
        char_vectors = char_vectorizer.fit_transform(char_texts)
        print(f"SET UP VECTORS")
    
    def get_most_similar(item, item_type):
        item_text = item['name']
        vectorizer = obj_vectorizer
        type_vectors = obj_vectors
        all_items = all_objects
        if item_type == "object":
            item_text += "\n" + item['physical_description']
        elif item_type == "character":
            item_text += "\n" + item['physical_description'] + "\n" + item['persona']
            vectorizer = char_vectorizer
            type_vectors = char_vectors
            all_items = all_chars
        else:
            item_text += "\n" + item['desc'] + "\n"
            vectorizer = room_vectorizer
            type_vectors = room_vectors
            all_items = all_rooms

        item_vec = vectorizer.transform([item_text])
        cosine_similarities = linear_kernel(item_vec, type_vectors).flatten()
        max_index = np.argmax(cosine_similarities)
        return all_items[max_index]

    def suggest_room(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ):
        # Use add_room_description and add_room_backstory to fill these
        # from a title alone
        print("SUGGEST ROOM")
        print(f"args: {args}")
        target_room = args["target_room"]
        room_graph = args["room_graph"]
        original_rooms = room_graph['rooms']
        if world_builder_agent is None or not USE_MODEL:
            print("No world builder model found, path does not point to file")
            if db is not None:
                print("using tfidf vectorizer to find similar room")
                print(f"USING ROOM: ")
                print(room_graph['nodes'][target_room])
                most_similar = get_most_similar(room_graph['nodes'][target_room], "room")
                print(most_similar)
                room_desc = most_similar['description']
                room_backstory = most_similar['backstory']
                room_graph['nodes'][target_room]['desc'] = room_desc
                room_graph['nodes'][target_room]['extra_desc'] = room_backstory
                room_graph['nodes'][target_room]['from_retrieval'] = True
            return room_graph
            
        try:
            room_graph['rooms'] = [r.replace(" ", "_") for r in room_graph['rooms']]
            room_graph['objects'] = [r.replace(" ", "_") for r in room_graph['objects']]
            room_graph['agents'] = [r.replace(" ", "_") for r in room_graph['agents']]

            # cur_room = room_graph['rooms']
            cur_room = target_room.replace(" ", "_")
            room_graph['rooms'] = [cur_room]
            cur_room = target_room.replace(" ", "_")
            
            print(f"cur_room {cur_room}")
            converted_graph = get_room_content_from_json(room_graph)
            print(f"converted graph")
            print(converted_graph)

            graph = world_builder_agent.add_room_description(converted_graph)
            graph = world_builder_agent.add_room_backstory(graph)
            print(f"Adding description: {graph['description']}")
            print(f"Adding backstory: {graph['background']}")
            room_graph = modify_room_attrs(room_graph, cur_room, "desc", graph["description"])
            room_graph = modify_room_attrs(room_graph, cur_room, "extra_desc", graph["background"])
        except Exception as e:
            print(f"Exception found:")
            print(e)
            print("Returning room graph at current stage")
            pass
        # final step, fix the room list
        room_graph['rooms'] = original_rooms
        return room_graph

    def suggest_room_contents(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ):
        room_graph = args["room_graph"]
        target_room = args["target_room"]
        original_rooms = room_graph['rooms']
        if world_builder_agent is None or not USE_MODEL:
            print("No world builder model found, path does not point to file")
            if db is not None:
                print("using tfidf vectorizer to find similar room")
                print(f"USING ROOM: ")
                print(room_graph['nodes'][target_room])
                most_similar = get_most_similar(room_graph['nodes'][target_room], "room")
                items_from_most_similar = ROOM_ID_TO_ITEMS[most_similar['id']]
                objects = items_from_most_similar['objects']
                characters = items_from_most_similar['characters']
                for o in objects:
                    o['container_node']['target_id'] = target_room
                    o['from_retrieval'] = True
                    node_id = o['node_id']
                    if node_id not in room_graph:
                        room_graph['nodes'][node_id] = o
                        room_graph['objects'].append(node_id)
                for c in characters:
                    c['container_node']['target_id'] = target_room
                    c['from_retrieval'] = True
                    node_id = c['node_id']
                    if node_id not in room_graph:
                        room_graph['nodes'][node_id] = c
                        room_graph['agents'].append(node_id)

            return room_graph
        try:
            room_graph['rooms'] = [r.replace(" ", "_") for r in room_graph['rooms']]
            room_graph['objects'] = [r.replace(" ", "_") for r in room_graph['objects']]
            room_graph['agents'] = [r.replace(" ", "_") for r in room_graph['agents']]

            cur_room = target_room.replace(" ", "_")
            room_graph['rooms'] = [cur_room]

            
            graph = get_room_content_from_json(room_graph)

            ########################
            # Add Object
            ########################
            graph, obj_name_diff = run_create_obj(graph, world_builder_agent, count=3)
            new_objects = [o for o in graph['objects'] if o['name'] in obj_name_diff]
            for o in new_objects:
                room_graph = add_object_to_graph(room_graph, cur_room, o)

            ########################
            # Add Character
            ########################
            graph, char_name_diff = run_create_char(graph, world_builder_agent, count=3)
            new_chars = [c for c in graph['characters'] if c['name'] in char_name_diff]
            for c in new_chars:
                room_graph = add_character_to_graph(room_graph, cur_room, c)
            print(f"new room graph")
            print(room_graph)
            print(f"new_chars: {[c['name'] for c in new_chars]}")
            print(f"new_objs: {[c['name'] for c in new_objects]}")
        except Exception as e:
            print(f"Exception found:")
            print(e)
            print("Returning room graph at current stage")
            pass
        # final step, fix the room list
        room_graph['rooms'] = original_rooms
        return room_graph

    def suggest_character_contents(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ):
        room_graph = args["room_graph"]
        target_room = args["target_room"]
        target_id = args["target_id"]
        if world_builder_agent is None or not USE_MODEL:
            print("No world builder model found, path does not point to file")
            return room_graph
        # Use `add_character_wearing`, `add_character_wielding`, `add_character_carrying`
        # to create three lists of suggestions
        try:
            room_graph['rooms'] = [r.replace(" ", "_") for r in room_graph['rooms']]
            room_graph['objects'] = [r.replace(" ", "_") for r in room_graph['objects']]
            room_graph['agents'] = [r.replace(" ", "_") for r in room_graph['agents']]

            cur_room = target_room.replace(" ", "_")
            original_rooms = room_graph['rooms']
            room_graph['rooms'] = [cur_room]

            target_id = args["target_id"]

            target_name = target_id
            for n, node in args["nodes"].items():
                if n == target_id:
                    target_name = node['name']
                    break
            
            graph = get_room_content_from_json(room_graph)

            character_dict = None
            for c in graph['characters']:
                if c['name'] == target_name:
                    character_dict = c
                    break
            original_carried = character_dict.get('carrying_objects', [])
            original_wielded = character_dict.get('wielding_objects', [])
            original_worn = character_dict.get('wearing_objects', [])

            graph = world_builder_agent.add_character_carrying(
                graph, target_name, count=3
            )
            graph = world_builder_agent.add_character_wearing(
                graph, target_name, count=3
            )
            graph = world_builder_agent.add_character_wielding(
                graph, target_name, count=3
            )
            character_dict = None
            for c in graph['characters']:
                if c['name'] == target_name:
                    character_dict = c
                    break
            
            # this should only modify 2 parts of the room graph
            # 1) contained_nodes section of the corresponding character
            # 2) the list of objects (which could contain more objects)
            carried = character_dict.get('carrying_objects', [])
            wielded = character_dict.get('wielding_objects', [])
            worn = character_dict.get('wearing_objects', [])
            new_carried = [o for o in carried if o not in original_carried]
            new_wielded = [o for o in wielded if o not in original_wielded]
            new_worn = [o for o in worn if o not in original_worn]

            graph = add_character_secondary_objects_to_graph(room_graph, target_id, new_carried, new_wielded, new_worn)
        except Exception as e:
            print(f"Exception found:")
            print(e)
            print("Returning room graph at current stage")
            pass
        # final step, fix the room list
        room_graph['rooms'] = original_rooms
        return room_graph

    def suggest_object_contents(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ):
        room_graph = args["room_graph"]
        target_room = args["target_room"]
        # Use `add_object_contains` to create a list of object suggestions
        target_id = args["target_id"]
        if world_builder_agent is None:
            print("No world builder model found, path does not point to file")
            return room_graph
        try:    
            room_graph['rooms'] = [r.replace(" ", "_") for r in room_graph['rooms']]
            room_graph['objects'] = [r.replace(" ", "_") for r in room_graph['objects']]
            room_graph['agents'] = [r.replace(" ", "_") for r in room_graph['agents']]

            cur_room = target_room.replace(" ", "_")
            original_rooms = room_graph['rooms']
            room_graph['rooms'] = [cur_room]

            graph = get_room_content_from_json(room_graph)

            # find the target object to get the underlying name
            target_name = target_id
            for n, node in args["nodes"].items():
                if n == target_id:
                    target_name = node['name']
                    break
            
            # find the corresponding object dict in the model-graph to get the contained objects
            object_dict = None
            for o in graph['objects']:
                if o['name'] == target_name:
                    object_dict = o
                    break
            
            original_contains = object_dict.get('containing_objects', [])
            
            # add objects to model-graph default number to attempt is 3
            graph = world_builder_agent.add_object_contains(
                graph, target_name, count=3
            )
            # find the corresponding object again, this time it will have the new contained objects
            object_dict = None
            for o in graph['objects']:
                if o['name'] == target_name:
                    object_dict = o
                    break
            
            # this should only modify 2 parts of the room graph
            # 1) contained_nodes section of the corresponding object
            # 2) the list of objects (which could contain more objects)
            contains = object_dict.get('carrying_objects', [])
            
            new_contains = [o for o in contains if o not in original_contains]
            
            graph = add_object_secondary_objects_to_graph(room_graph, target_id, new_contains)
        except Exception as e:
            print(f"Exception found:")
            print(e)
            print("Returning room graph at current stage")
            pass
        # final step, fix the room list
        room_graph['rooms'] = original_rooms
        return room_graph

    def fill_object(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ):
        # Fill the attributes and contents of object_id with `add_all_static_attributes`
        # and `add_all_object_attributes`
        room_graph = args["room_graph"]
        target_room = args["target_room"]
        target_id = args["object_id"]
        if world_builder_agent is None:
            print("No world builder model found, path does not point to file")
            return room_graph

        room_graph['rooms'] = [r.replace(" ", "_") for r in room_graph['rooms']]
        room_graph['objects'] = [r.replace(" ", "_") for r in room_graph['objects']]
        room_graph['agents'] = [r.replace(" ", "_") for r in room_graph['agents']]

        cur_room = target_room.replace(" ", "_")
        original_rooms = room_graph['rooms']
        room_graph['rooms'] = [cur_room]

        graph = get_room_content_from_json(room_graph)

        target_name = target_id
        for n, node in args["nodes"].items():
            if n == target_id:
                target_name = node['name']
                break
        
        graph = world_builder_agent.add_all_object_attributes(
            graph, target_name, count=3
        )


        room_graph['rooms'] = original_rooms
        return room_graph

    def fill_character(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ):
        # Fill the attributes and contents of character_id with `add_all_character_attributes`
        room_graph = args["room_graph"]
        room_graph = args["character_id"]
        if world_builder_agent is None:
            print("No world builder model found, path does not point to file")
            return room_graph
        return room_graph

    def fill_room(
        _request_id: str, args: Dict[str, Any], agent_state: RemoteProcedureAgentState
    ):
        # Use add_object, add_character, fill_object, and fill_character to fill out this room
        room_graph = args["room_graph"]
        if world_builder_agent is None:
            print("No world builder model found, path does not point to file")
            return room_graph
        return room_graph

    function_registry = {
        "suggest_room_contents": suggest_room_contents,
        "suggest_character_contents": suggest_character_contents,
        "suggest_object_contents": suggest_object_contents,
        "suggest_room": suggest_room,
        "fill_object": fill_object,
        "fill_character": fill_character,
        "fill_room": fill_room,
    }

    shared_state = SharedRemoteProcedureTaskState(
        static_task_data=tasks,
        function_registry=function_registry,
        validate_onboarding=validate_onboarding,
        on_unit_submitted=validate_unit,
    )

    task_dir = cfg.task_dir
    build_custom_bundle(task_dir)

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
