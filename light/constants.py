#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os

LIGHT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
LIGHT_DATAPATH = os.path.join(LIGHT_PATH , "data")


def _parlai_dir():
    from parlai import __path__ as parlai_path_list
    return os.path.join(parlai_path_list[0], "..")


PARLAI_PATH = _parlai_dir()