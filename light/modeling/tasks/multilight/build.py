#!/usr/bin/env python3

# Copyright (c) Meta, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from collections import defaultdict
import json
import jsonlines
import os
from tqdm import tqdm
from typing import Any, Dict, List

import parlai.core.build_data as build_data
import parlai.utils.logging as logging

from light.constants import LIGHT_DATAPATH
from light.data_model.db.base import LightDBConfig, DBSplitType
from light.data_model.db.episodes import EpisodeDB
from light.modeling.tasks.multilight import constants


DATA_PATH = os.path.join(LIGHT_DATAPATH, constants.DEFAULT_DATASET_SUBPATH)


def get_personas(graph: Dict[str, Any]) -> List[Dict[str, str]]:
    personas = []
    for p in graph.get_humans():
        personas.append({"name": p.name, "persona": p.persona})
    return personas


def read_episodes_from_db() -> Dict[DBSplitType, List[Dict[str, Any]]]:
    db_path = os.path.join(DATA_PATH, "episode.db")
    assert os.path.exists(db_path), (
        f"No EpisodeDB  found at {db_path}. "
        "Make sure you have downloaded the updated EpisodeDB."
    )
    db_conf = LightDBConfig(backend="local", file_root=DATA_PATH)
    db = EpisodeDB(db_conf)
    db_episodes = db.get_episodes()
    logging.info(
        f"Processing a total of {len(db_episodes)} episodes from the EpisodeDB."
    )
    data_splits = defaultdict(list)
    for episode_data in tqdm(db_episodes):

        conv_file = os.path.join(
            LIGHT_DATAPATH,
            constants.DEFAULT_DATASET_SUBPATH,
            episode_data.dump_file_path,
        )
        with open(conv_file, "r") as fi:
            episodes_dump_data = json.load(fi)

        conv = {
            "messages": [],
            "characters": get_personas(episode_data.get_before_graph(db)),
        }
        for ei, game_event in enumerate(episodes_dump_data["events"]):
            utt_data = json.loads(game_event["event_json"])
            if ei == 0:
                # Setting the location and quality tier from the first message
                conv["quality_tier"] = utt_data["room"]["data_quality_tier"]
                conv["location"] = {
                    "name": utt_data["room"]["name"],
                    "description": utt_data["room"]["extra_desc"],
                }

            # Adding the messages
            conv["messages"].append(
                {
                    "speaker": utt_data["actor"]["name"],
                    "timestamp": utt_data["event_time"],
                    "text": utt_data["text_content"],
                    "workers_tier": utt_data["actor"]["tier"],
                }
            )

        data_splits[episode_data.split].append(conv)
    return data_splits


def build():
    processed_dpath = os.path.join(DATA_PATH, constants.PROCESSED_FILES_DIRNAME)
    version = "0.1"
    if not build_data.built(processed_dpath, version):
        logging.info(
            f"[building data: {processed_dpath}]\nThis may take a while but only heppens once."
        )
        if build_data.built(processed_dpath):
            # An older version exists, so remove these outdated files.
            build_data.remove_dir(processed_dpath)
        build_data.make_dir(processed_dpath)

        extracted_data_splits = read_episodes_from_db()
        for dsplt, conv_data in extracted_data_splits.items():
            logging.info(f"Storing {len(conv_data)} processed data for {dsplt}")
            with jsonlines.open(
                os.path.join(processed_dpath, f"{dsplt.value}.jsonl"), "w"
            ) as fo:
                for conv in conv_data:
                    fo.write(conv)

        logging.info("Finished creating the processed dataset files successfully.")

        build_data.mark_done(processed_dpath, version)
