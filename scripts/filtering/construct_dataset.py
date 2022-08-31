#!/usr/bin/env python3


# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
    This file is responsible for transforming the event logs into datasets.
    Since we have two POVs, may need different logic

    So, given a log(s):
        1. Load the log (see reconstruct_logs)
        2. Get the log's episodes (see extract_episodes.py)
        3. Write to the dataset
        4. Export the dataset, adding any necessary metadata

    example usage:
        python scripts/filtering/construct_dataset.py --log-dir ./logs
            --dataset-dir ./dataset/
"""
from scripts.filtering.reconstruct_logs import load_event_log
from scripts.filtering.extract_episodes import extract_episodes, EpisodeEncoder
import argparse
import json
import os
import time


def convert_event_log_dirs(event_log_dir, dataset_dir):
    """
    Given a directory which may contain log files, search for all the
    log files inside this directory and extract the episodes from each
    of them using convert_event_log
    """
    for subdir, _, files in os.walk(event_log_dir):
        for filename in files:

            filepath = subdir + os.sep + filename
            if filepath.endswith("events.log"):
                convert_event_log(filepath, dataset_dir)


def convert_event_log(event_file, dataset_dir):
    """
    Given a log file and a dataset directory to write to, extract the
    training episodes from the log and write them to the dataset.
    """
    uuid_to_world, event_buffer = load_event_log(
        event_file,
    )
    # TODO: Have a better way to say if log is agent or room POV (?)
    agent_pov = "agent" in os.path.abspath(os.path.dirname(event_file))
    try:
        episodes = extract_episodes(uuid_to_world, event_buffer, agent_pov=agent_pov)
    except:
        # Seems death/health events are doing wierd things when executing?
        # No health attribute?
        print("Encountered an unexpected error when extracting")
        print(event_file)
        return
    write_episodes_to_dir(episodes, dataset_dir)


def write_episodes_to_dir(episodes, dataset_dir, indent=4):
    """
    Given episodes and a directory for a dataset, write the episodes to the dataset
    """
    if not os.path.exists(dataset_dir):
        os.mkdir(dataset_dir)

    # Decide what to do with the naming - random right now
    for episode in episodes:
        # Convention is actor + starting room + time
        first_room = str(list(episode.settings.keys())[0])
        unique_name = " ".join([episode.actor, first_room, str(time.time())])
        file_name = f"{unique_name}.txt".replace(" ", "_")
        # Wierd bug with an agent named horse_caretaker/trainer
        file_name = file_name.replace("'", "").replace("/", "")
        file_path = os.path.join(dataset_dir, file_name)
        with open(file_path, "w") as episode_file:
            episode_dict = {k: v for k, v in episode.__dict__.copy().items()}
            res = json.dumps(
                episode_dict, cls=EpisodeEncoder, sort_keys=True, indent=indent
            )
            episode_file.write(res)


def main():
    parser = argparse.ArgumentParser(
        description="Args for the directory of log to convert"
    )

    parser.add_argument(
        "--dataset-dir",
        type=str,
        help="The directory to put the episodes",
        required=True,
    )

    # Only have one of a log or directory of logs
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--event-log", type=str, help="The event log to convert")
    group.add_argument(
        "--log-dir", type=str, help="The top level directory of event logs to convert"
    )

    FLAGS, _unknown = parser.parse_known_args()
    if FLAGS.log_dir is not None:
        convert_event_log_dirs(FLAGS.log_dir, FLAGS.dataset_dir)
    elif FLAGS.event_log is not None:
        convert_event_log(FLAGS.event_log, FLAGS.dataset_dir)
    else:
        print("Must provide an individual event log or a directory to construct")
        print("Please try again")


if __name__ == "__main__":
    main()
