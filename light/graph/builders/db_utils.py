# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.data_model.light_database import (
    LIGHTDatabase,
    DB_STATUS_REJECTED,
    DB_TRAIN_SPLIT,
    DB_TEST_SPLIT,
    DB_VAL_SPLIT,
)
import random


def id_is_usable(ldb, id_to_check):
    """Check response of get_id to see if id_entry
    exists andis not of 'rejected' status"""
    id_entry = ldb.get_id(id=id_to_check)
    # TODO:  Have dev vs prod mode, change rejected and prod depending on mode
    if len(id_entry) <= 0 or id_entry[0]["status"] == DB_STATUS_REJECTED:
        return False
    return True


def assign_datasplit(db_path, db_type, weights=[0.8, 0.1, 0.1]):
    """Assign datasplit given a speicific database type based
    on given weights. Only assign datasplit to unassigned entries"""
    with LIGHTDatabase(db_path, True) as ldb:
        id_entries = ldb.get_id(type=db_type)
        unassigned_id = [entry["id"] for entry in id_entries if entry["split"] is None]
        for id in unassigned_id:
            split = random.choices(
                [DB_TRAIN_SPLIT, DB_TEST_SPLIT, DB_VAL_SPLIT], weights=weights
            )[0]
            ldb.update_split(id, split)
