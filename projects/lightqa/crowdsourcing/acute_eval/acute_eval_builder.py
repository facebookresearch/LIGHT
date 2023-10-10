#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os

from parlai.crowdsourcing.tasks.acute_eval.acute_eval_builder import AcuteEvalBuilder


class LightQAAcuteBuilder(AcuteEvalBuilder):
    """
    Subclass of AcuteEvalBuilder to specify a local frontend build directory.
    """

    ACUTE_TASK_DIR = os.path.dirname(os.path.abspath(__file__))
    FRONTEND_SOURCE_DIR = os.path.join(ACUTE_TASK_DIR, "webapp")
    FRONTEND_BUILD_DIR = os.path.join(FRONTEND_SOURCE_DIR, "build")
