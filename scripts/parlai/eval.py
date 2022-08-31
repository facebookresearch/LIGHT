#!/usr/bin/env python3
"""
Basic example which iterates through the tasks specified and evaluates the given model
on them.
For more documentation, see parlai.scripts.eval_model.
"""
from parlai.scripts.eval_model import EvalModel
import light.modeling.loading as load

load.register_all_agents()
load.register_all_tasks()

if __name__ == "__main__":
    EvalModel.main()
