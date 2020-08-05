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
import os
import uuid


def convert_event_log_dirs(event_log_dir, dataset_dir):
    """
        Given a directory which may contain log files, search for all the
        log files inside this directory and extract the episodes from each
        of them using convert_event_log
    """
    conversion_count = 0
    for subdir, dirs, files in os.walk(event_log_dir):
        for filename in files:

            filepath = subdir + os.sep + filename
            if filepath.endswith("events.log"):
                conversion_count += 1
                convert_event_log(filepath, dataset_dir)


def convert_event_log(event_file, dataset_dir):
    """
        Given a log file and a dataset directory to write to, extract the
        training episodes from the log and write them to the dataset.
    """
    print(event_file)
    uuid_to_world, event_buffer = load_event_log(event_file,)
    episodes = extract_episodes(uuid_to_world, event_buffer)
    write_episodes_to_dir(episodes, dataset_dir)


def write_episodes_to_dir(episodes, dataset_dir):
    """
        Given episodes and a directory for a dataset, write the episodes to the dataset
    """
    if not os.path.exists(dataset_dir):
        os.mkdir(dataset_dir)

    # Decide what to do with the naming - random right now
    for episode in episodes:
        unique_name = str(uuid.uuid4())
        file_name = f"{unique_name}.txt"
        file_path = os.path.join(dataset_dir, file_name)
        with open(file_path, "w") as episode_file:

            # TODO - need any other metadata?  How to tag metadata
            # with the name perhaps?
            episode_file.write("_setting_name   " + episode._setting_name + "\n")
            episode_file.write("_setting_desc   " + episode._setting_desc + "\n")
            episode_file.write("\n")

            episode_file.write("\n_agents:\n")
            for agent_name in episode.agents:
                episode_file.write("_name   " + agent_name + "\n")
                episode_file.write("_persona  " + episode.agents[agent_name] + "\n\n")

            # TODO: Decide if need objects or not
            episode_file.write("\n_dialogue\n")
            for utter in episode.utterances:
                # Fill in what to write properly - should be line by line?
                # CSV?  Tab seperated?
                episode_file.write("_actor  " + utter.actor_id + "\n")
                if utter.text is not None:
                    episode_file.write("_msg_text   " + utter.text + "\n")
                if utter.action is not None:
                    episode_file.write("_msg_act   " + utter.action + "\n")
                if utter.target_ids is not None:
                    for target_id in utter.target_ids:
                        episode_file.write("_target " + target_id + "\n")
                episode_file.write("\n")
            episode_file.write("_episode_done true")


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
