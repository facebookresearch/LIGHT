#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
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
"""
from scripts.filtering.reconstruct_logs import load_event_log
from scripts.filtering.extract_episodes import extract_episodes
import argparse


def convert_event_log(event_file, dataset_dir):
    """
        Given a log file and a dataset directory to write to, extract the
        training episodes from the log and write them to the dataset.
    """
    uuid_to_world, event_buffer = load_event_log(event_file,)
    episodes = extract_episodes(uuid_to_world, event_buffer)
    write_episodes_to_dir(episodes, dataset_dir)


def write_episodes_to_dir(episodes, dataset_dir):
    """
        Given episodes and a directory for a dataset, write the episodes to the dataset
    """
    for episode in episodes:
        for utter in episode.convo:
            print(utter.actor_id, "said")
            print(utter.text)
    pass


def main():
    parser = argparse.ArgumentParser(
        description="Args for the directory of log to convert"
    )
    parser.add_argument("--event-log", type=str, help="The event log to convert")
    parser.add_argument(
        "--dataset-dir", type=str, help="The directory to put the episodes"
    )
    FLAGS, _unknown = parser.parse_known_args()
    convert_event_log(FLAGS.event_log, FLAGS.dataset_dir)


if __name__ == "__main__":
    main()
