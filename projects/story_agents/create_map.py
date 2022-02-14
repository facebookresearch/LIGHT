#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Simple example script that demonstrates initializing and using a world builder.

Writes the output file in the .json format for use in other scripts

Derived and simplified from /scripts/gen_map.py
"""

import os
from light import LIGHT_DIR
from example_builder import ExampleBuilder
import light.modeling.tasks.utils as utils
from parlai.core.build_data import DownloadableFile
from light.data_model.light_database import LIGHTDatabase
from parlai.core.params import ParlaiParser

BASE_DPATH = os.path.join(LIGHT_DIR, "data")
LIGHT_DB_FILE_LOC = os.path.join(LIGHT_DIR, "data", "env", "database3.db")
CURR_DIR = os.path.dirname(__file__)

if not os.path.exists(LIGHT_DB_FILE_LOC):
    dl_file = DownloadableFile(
        "http://parl.ai/downloads/light_project/env/database3.db",
        "env/database3.db",
        "ed6b0c6b97b9ccd7a3083f690fa322c7dd7a33c628a5f72dc6c4ab57ff8666aa",
        zipped=False,
    )
    utils.download_for_light(BASE_DPATH, dl_file)

if __name__ == "__main__":
    parser = ParlaiParser()
    parser.add_argument("--out-file", type=str, default="map.json")
    ExampleBuilder.add_parser_arguments(parser)
    opt, _unknown = parser.parse_and_process_known_args()
    print("[loading db...]")
    ldb = LIGHTDatabase(LIGHT_DB_FILE_LOC)
    print("[loading builder model...]")
    world_builder = ExampleBuilder(ldb, debug=False, opt=opt)
    print("[Building light graph]")
    g, world = world_builder.get_graph()
    data = g.to_json()
    target_loc = os.path.join(CURR_DIR, "outputs", opt["out_file"])
    with open(target_loc, "w+") as mapfile:
        print(f"[Writing out file to {target_loc}]")
        mapfile.write(data)
