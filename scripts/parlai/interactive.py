#!/usr/bin/env python3
"""
Basic example which allows local human keyboard input to talk to a trained model.
For documentation, see parlai.scripts.interactive.
"""
import random
from parlai.scripts.interactive import Interactive
import light.modeling.loading as load

load.register_all_agents()
load.register_all_tasks()


if __name__ == "__main__":
    random.seed(42)
    Interactive.main()
