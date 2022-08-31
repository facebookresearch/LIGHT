#!/usr/bin/env python3
"""
Basic example which iterates through the tasks specified and prints them out. Used for
verification of data loading and iteration.
For more documentation, see parlai.scripts.display_data.
"""

import random
from parlai.scripts.display_data import DisplayData
import light.modeling.loading as load

load.register_all_agents()
load.register_all_tasks()


if __name__ == "__main__":
    random.seed(42)
    DisplayData.main()
