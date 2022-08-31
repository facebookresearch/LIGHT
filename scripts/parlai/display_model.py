#!/usr/bin/env python3
"""
Basic script to display the arguments and setup for a given model
For more documentation, see parlai.scripts.display_model.
"""

from parlai.scripts.display_model import display_model, setup_args
import light.modeling.loading as load

load.register_all_agents()
load.register_all_tasks()

if __name__ == "__main__":
    parser = setup_args()
    opt = parser.parse_args()
    display_model(opt)
