#!/usr/bin/env python3
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
