#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from os.path import abspath, dirname
from light.registry.hydra_registry import initialize_named_configs

# Path to LIGHT GIHUB dir
LIGHT_DIR = dirname(dirname(abspath(__file__)))
initialize_named_configs()
