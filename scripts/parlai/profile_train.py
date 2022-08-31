#!/usr/bin/env python3
"""
Train a model using parlai's standard training loop.
For documentation, see parlai.scripts.profile_train.
"""
from parlai.scripts.profile_train import ProfileTrain
import light.modeling.loading as load

load.register_all_agents()
load.register_all_tasks()

if __name__ == "__main__":
    ProfileTrain.main()
