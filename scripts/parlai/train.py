#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""
Train a model using parlai's standard training loop.
For documentation, see parlai.scripts.train_model.
"""
from parlai.scripts.train_model import TrainModel
import light.modeling.loading as load

load.register_all_agents()
load.register_all_tasks()


if __name__ == "__main__":
    TrainModel.main()
