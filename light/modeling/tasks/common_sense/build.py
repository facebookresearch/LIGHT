#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""
Builds the dataset for commmon sense project in LIGHT.
"""

from collections import defaultdict
from copy import deepcopy
import pickle
import jsonlines
import os
import shutil
from tqdm import tqdm
import parlai.core.build_data as build_data
from parlai.utils.data import DatatypeHelper
import parlai.utils.logging as logging
import light.modeling.tasks.common_sense.constants as consts

import random

random.seed(8)


try:
    from light.graph.builders.base import DBGraphBuilder
    from light.graph.structured_graph import OOGraph
    from light.world.world import World
    from light.data_model.light_database import (
        LIGHTDatabase,
    )

except ModuleNotFoundError:
    raise ModuleNotFoundError(consts.INST_LIGHT_MSG)


def get_dtype(opt):
    return DatatypeHelper.fold(opt["datatype"])


def reproducable_sample(arr, n=consts.SELF_PLAY_ACTIONS_SAMPLE_SIZE):
    """
    Sample from the sorted copy of arr on equal-spaced intervals.

    For reproducable down-sampling of large data.
    NOTE: make sure that the seed is set appropriately. Lucky number 8.
    """
    if len(arr) <= n:
        return arr
    return random.sample(arr, k=n)


class RoomCommonSenseGraphBuilder(DBGraphBuilder):
    def __init__(self, db_path, allow_blocked=False):
        logging.info(f'Opening the LIGHT DB at "{db_path}"')
        ldb = LIGHTDatabase(db_path, True)
        logging.info("DB opened successfully.")
        super().__init__(ldb, allow_blocked)


class ExampleGameplayWorld(World):
    def __init__(self, graph):
        super().__init__(graph._opt, None)
        self.oo_graph = graph

    @staticmethod
    def from_graph(graph):
        """
        Loads the world from the older versions of graph.
        """
        oo_graph = OOGraph.from_graph(graph)
        world = ExampleGameplayWorld(oo_graph)
        world._node_freeze = graph._node_freeze
        return world

    def get_node_from_id(self, node_id):
        return self.oo_graph.get_node(node_id)

    def get_game_engine_graph(self):
        return self.oo_graph.to_json()


def _get_element_attributes(db_element, attributes_list):
    data = dict()
    for att in attributes_list:
        data[att] = db_element.__dict__.get(att)
    return data


def get_room_data(db_room):
    """
    Outputs a dict containing relevant data from a DBRoom object.
    """
    data = _get_element_attributes(db_room, consts.ROOM_ATTRIBUTES)
    if data["data_split"] == "val":
        data["data_split"] = "valid"
    # The following lists are place-holder. They will be populated later.
    data.update({"objects": [], "characters": []})
    data["element_type"] = "room"
    return data


def get_object_data(db_object):
    """
    Outputs a dict containing relevant data from a DBObject object.
    """
    object_data = _get_element_attributes(db_object, consts.ROOM_OBJECT_ATTRIBUTES)
    # For some reason I don't know I can't get lists with the above function.
    object_data["containing_objects"] = db_object.containing_objs
    object_data["contained_by"] = db_object.contained_by
    object_data["element_type"] = "objects"
    return object_data


def get_character_data(db_character, graph_builder):
    """
    Outputs a dict containing relevant data from a DBCharacter object.
    """

    def get_related_objects(related_objects_ids):
        related_objects = []
        for ro_id in related_objects_ids:
            ro = graph_builder.get_obj_from_id(ro_id)
            related_objects.append(
                _get_element_attributes(ro, consts.ROOM_OBJECT_ATTRIBUTES)
            )
        return related_objects

    character_data = _get_element_attributes(
        db_character, consts.ROOM_CHARACTER_ATTRIBUTES
    )
    # For some reason I don't know I can't get lists with the above function.
    character_data["carrying_objects"] = get_related_objects(
        db_character.carrying_objects["db"]
    )
    character_data["wearing_objects"] = get_related_objects(
        db_character.wearing_objects["db"]
    )
    character_data["wielding_objects"] = get_related_objects(
        db_character.wielding_objects["db"]
    )
    character_data["element_type"] = "characters"
    return character_data


def split_rooms(graph_builder):
    """
    Outputs a map from data types to the room data.
    """
    split_room_data = {"train": [], "valid": [], "test": []}
    usable_rooms = graph_builder.get_usable_rooms()
    for db_room_id in tqdm(usable_rooms):
        room_data = graph_builder.get_room_from_id(db_room_id)
        splt = room_data.data_split
        if splt == "val":
            splt = "valid"
        split_room_data[splt].append(db_room_id)
    logging.info(
        "Room splits: "
        " == ".join([f"{k}: {len(v)}" for (k, v) in split_room_data.items()])
    )
    return split_room_data


def get_room_and_content_data(
    graph_builder,
):
    """
    Outptus a dictionary with the data about the rooms and its content (characters and
    objects)
    """
    room_splits = split_rooms(graph_builder)
    train_seen_items = defaultdict(set)

    def seen_by_train_set(dt, item_type, db_id):
        """
        Whether to tag an item as seen in the train data.
        """
        if dt == "train":
            train_seen_items[item_type].add(db_id)
        return db_id in train_seen_items[item_type]

    logging.info("Extracting rooms/settings data.")
    data_splits = dict()
    for dtype in ("train", "valid", "test"):
        data_splits[dtype] = []
        for db_room_id in room_splits[dtype]:
            room = graph_builder.get_room_from_id(db_room_id)
            room_data = get_room_data(room)

            # Getting the list of objects in the room
            in_room_object_ids = room.in_objects["db"]
            ex_room_object_ids = room.ex_objects["db"]
            for room_object_id in in_room_object_ids + ex_room_object_ids:
                room_object = graph_builder.get_obj_from_id(room_object_id)
                if not room_object:
                    continue
                room_object_data = get_object_data(room_object)
                room_object_data[consts.IS_IN_ROOM] = (
                    room_object_id in in_room_object_ids
                )
                room_object_data[consts.SEEN_IN_TRAIN_DATA] = seen_by_train_set(
                    dtype, "objects", room_object_id
                )
                room_data["objects"].append(room_object_data)

            # Getting the list of characters in the room
            in_room_character_ids = room.in_characters["db"]
            ex_room_character_ids = room.ex_characters["db"]
            for room_character_id in in_room_character_ids + ex_room_character_ids:
                room_characetr = graph_builder.get_char_from_id(room_character_id)
                if not room_characetr:
                    continue
                room_characetr_data = get_character_data(room_characetr, graph_builder)
                room_characetr_data[consts.IS_IN_ROOM] = (
                    room_character_id in in_room_character_ids
                )
                room_characetr_data[consts.SEEN_IN_TRAIN_DATA] = seen_by_train_set(
                    dtype, "characters", room_character_id
                )
                room_data["characters"].append(room_characetr_data)

            data_splits[dtype].append(room_data)

    return data_splits


def generate_room_data(graph_builder, output_dir):
    """
    Fetches data about rooms and their content and stores them in `output_dir`
    """
    build_data.make_dir(output_dir)
    rc_data = get_room_and_content_data(graph_builder)
    logging.info(f"Room data summary: {[(k, len(v)) for k, v in rc_data.items()]}")
    for dk, dv in rc_data.items():
        dtype = "valid" if dk == "val" else dk
        with jsonlines.open(os.path.join(output_dir, f"{dtype}.jsonl"), "w") as fo:
            for room_content_data in dv:
                fo.write(room_content_data)


def download_dataset(dpath):
    """
    Fetches the raw dataset.
    """
    # Copyig the DB
    logging.info("Downloading (copying) the database.")
    shutil.copy(consts.ORIGINAL_LIGHT_DB_ADDRESS, dpath)

    # Downloading (copying) the gameplay dataset
    logging.info("Downloading (copying) the game play dataset.")
    gameplay_dir = os.path.join(dpath, consts.GAMEPLAY_DIR)
    build_data.make_dir(gameplay_dir)
    for data_split in consts.GAMEPLAY_SPLITS:
        source_fpath = os.path.join(
            consts.ORIGINAL_LIGHT_GAMEPLAY_PATH, f"{data_split}_convs.pkl"
        )
        shutil.copy(source_fpath, gameplay_dir)


def generate_all_potential_actions(game_world, acting_agent):
    potential_actions = []
    for event in consts.POTENTIAL_EVENTS_TO_CHECK:
        for target_node_id in game_world.all_node_ids():
            targer_node = game_world.get_node_from_id(target_node_id)
            if acting_agent == targer_node:
                continue
            object_container_node = targer_node.container_node.get()
            event_act = event(
                actor=acting_agent, target_nodes=[targer_node, object_container_node]
            )
            potential_actions.append(event_act.to_canonical_form())
    return set(potential_actions)


def run_gameplay(gameplay_data):
    """
    Runs a play through of the game actions as done by crowdsourcers.
    """

    def get_agent_last_observation(agent_node):
        return agent_node._observations[-1].view_as(agent_node)

    conv_info = gameplay_data["conv_info"]
    ret_data = []

    # NOTE the dataset is using the old version of graph
    gameplay_world = ExampleGameplayWorld.from_graph(gameplay_data["graph"])
    last_game_state = None
    for conv in conv_info["acts"]:
        round_action = dict()
        ret_data.append(round_action)
        current_acting_agent = conv["id"]
        round_action["speaker_id"] = current_acting_agent
        round_action["speech_text"] = conv["text"]
        round_action[
            "game_state_before_action"
        ] = gameplay_world.get_game_engine_graph()

        task_data = conv["task_data"]
        world_player_agent = gameplay_world.get_node_from_id(
            current_acting_agent.lower()
        )

        # Running the player action and recording the state of the game after that
        round_act = task_data["action"]
        round_action["action"] = round_act
        round_action["player_context"] = task_data["text_context"]
        round_action["game_state_after_action"] = None
        if not round_act:
            # No action that causes the change in the game graph.
            # NOTE: we also only run self-plays when there are game actions because otherwise
            # there will be numerous repeated staring points for self-plays.
            continue

        gameplay_world.parse_exec(world_player_agent, round_act)
        round_action["agent_observation"] = get_agent_last_observation(
            world_player_agent
        )
        game_state_after_action = gameplay_world.get_game_engine_graph()
        round_action["game_state_after_action"] = game_state_after_action

        # Adding potential actions
        possible_actions = task_data["actions"]
        round_action["possible_actions"] = possible_actions

        #########
        # Self-play actions
        if last_game_state and last_game_state == game_state_after_action:
            # We have done self-play on this state before
            continue
        last_game_state = game_state_after_action

        all_potential_actions = generate_all_potential_actions(
            gameplay_world, world_player_agent
        )
        invalid_actions = list(all_potential_actions - set(possible_actions))

        # One step game play with possible and invalid actions
        parallel_world_plays = []
        sampled_rollout_actions = reproducable_sample(
            possible_actions
        ) + reproducable_sample(invalid_actions)
        for potential_act in sampled_rollout_actions:
            # A parallel game world that actions have no consequence on the main world.
            # For this to make sense, go and watch Rick and Morty: The Vat of Acid episode
            copy_world = ExampleGameplayWorld(deepcopy(gameplay_world.oo_graph))
            copy_world_agent = copy_world.get_node_from_id(current_acting_agent.lower())
            copy_world.parse_exec(copy_world_agent, potential_act)
            parallel_world_plays.append(
                {
                    "action": potential_act,
                    "game_state_after_action": copy_world.get_game_engine_graph(),
                    "agent_observation": get_agent_last_observation(copy_world_agent),
                }
            )

        round_action[consts.ONE_LEVEL_SELF_PLAY_KEY] = parallel_world_plays

    return ret_data


def generate_gameplay_data(dpath):
    def skip_convo(splt, idx):
        """
        Convos with inconsistent data that crash the game World.
        """
        convos_to_skip = {"train": (7988, 8280)}
        return idx in convos_to_skip.get(splt, [])

    for data_split in consts.GAMEPLAY_SPLITS:
        fname = f"{data_split}_convs"
        fpath = os.path.join(dpath, consts.GAMEPLAY_DIR, f"{fname}.pkl")
        logging.info(f"Populating {data_split} data split in {fpath}.")
        out_data = []

        # Opening dataset and running play throughs
        with open(fpath, "rb") as fin:
            for idx, conv in enumerate(tqdm(pickle.load(fin))):
                if skip_convo(data_split, idx):
                    continue
                out_data.append(run_gameplay(conv))

        # Storing the output data
        output_fname = f"processed_{fname}"
        with jsonlines.open(
            os.path.join(dpath, consts.GAMEPLAY_DIR, f"{output_fname}.jsonl"), "w"
        ) as fout:
            for episode in out_data:
                fout.write(episode)


def build(opt):
    cs_dpath = os.path.join(opt["datapath"], consts.DATASET_DIR_NAME)
    version = "2.12"
    if build_data.built(cs_dpath, version_string=version):
        # The dataset is already there; no need to build it again.
        return

    ##################################################
    #
    #   Generating room (world builder) data
    #
    ##################################################
    logging.info(f"Building the dataset in {cs_dpath}")

    if build_data.built(cs_dpath):
        # An older version exists, so remove these outdated files.
        build_data.remove_dir(cs_dpath)
    build_data.make_dir(cs_dpath)
    download_dataset(cs_dpath)
    db_path = os.path.join(cs_dpath, "database3.db")
    room_cs_graph_builder = RoomCommonSenseGraphBuilder(db_path, True)
    generate_room_data(
        room_cs_graph_builder, os.path.join(cs_dpath, consts.ROOM_CONTENTS_DIR)
    )
    generate_gameplay_data(cs_dpath)

    build_data.mark_done(cs_dpath, version_string=version)
