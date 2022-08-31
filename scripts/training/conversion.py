#!/usr/bin/env python3


# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
    This file is responsible for converting the training conversations of the
    old pickle format into the new format using the construct_dataset

    example usage:
        python scripts/training/conversion.py --file ../valid_convs.pkl
            --log-dir ./logs --dataset-dir ./dataset/
"""
import argparse
import pickle
import os
import asyncio
from light.graph.structured_graph import OOGraph
from light.world.world import World, WorldConfig
from light.graph.events.graph_events import SoulSpawnEvent, LookEvent
from scripts.filtering.construct_dataset import convert_event_log_dirs


def execute_events(world, transcript):
    """
    Attempts to parse and execute the events contained in the transcript
    """
    for event in transcript:
        # parse exec, then execute according to
        # gesture -> emote "xyz"
        # text -> say/tell (?)
        # other actions are literals
        action = event["task_data"]["action"]
        if action != "":
            if action.startswith("gesture"):
                action = action.replace("gesture", "emote")
            asyncio.run(world.parse_exec(event["id"].lower(), action))
        asyncio.run(world.parse_exec(event["id"].lower(), "say " + event["text"]))


def process_episodes(src, log_dir):
    """
    Reconstructs the episodes contained in src and executes them,
    resulting in new logs
    """
    # alt is, everything contained in room so just room logger is fine
    # Room logger - is_player already specified (nice!)
    i = 0
    for ep in src:
        ep["graph"]._opt["is_logging"] = True
        ep["graph"]._opt["log_path"] = log_dir
        new_g = OOGraph.from_graph(ep["graph"])
        world = World(WorldConfig(opt=new_g._opt))
        world.oo_graph = new_g
        transcript = ep["conv_info"]["acts"]
        players = [x for x in new_g.all_nodes.values() if x.agent and x.is_player]
        # Init the required for constructing dataset
        for p in players:
            SoulSpawnEvent(p.node_id, p).execute(world)
            LookEvent(p).execute(world)
        try:
            execute_events(world, transcript)
        except:
            with open(f"./error{i}.pkl", "wb") as picklefile:
                pickle.dump(ep, picklefile)
            print("Found an error in executing, writing out")
            i += 1
        for log in new_g.room_id_to_loggers.values():
            log._end_meta_episode()


def main():
    parser = argparse.ArgumentParser(description="Args for the conversion of pkl file")
    parser.add_argument("--file", type=str, help="The file to convert")
    parser.add_argument(
        "--log-dir", type=str, help="The log directory to write logs to"
    )
    parser.add_argument(
        "--dataset-dir",
        type=str,
        help="The directory to write newly constructed dataset to",
    )

    FLAGS, _unknown = parser.parse_known_args()
    with open(FLAGS.file, "rb") as pkl:
        og = pickle.load(pkl)
        process_episodes(og, FLAGS.log_dir)
    out_room_logs = os.path.join(FLAGS.log_dir, "light_event_dumps/room")
    convert_event_log_dirs(out_room_logs, FLAGS.dataset_dir)


if __name__ == "__main__":
    main()
