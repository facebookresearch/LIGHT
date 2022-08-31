#!/usr/bin/env python3


"""
Main launch script for single-host, multi-GPU evaluation.
This is a drop-in replacement for eval_model.  This script will launch N
subprocess, each which runs the full eval loop independently.
Uses torch.nn.parallel.DistributedDataParallel for its main uses.  Agents must
specifically implement the wrapper of DistributedDataParallel, but all
TorchRankerAgents and TorchGeneratorAgents support this.
Examples
--------
.. code-block:: shell
  parlai multiprocessing_eval -mf "zoo:tutorial_transformer_generator/model" -bs 16 -t convai2
"""

from parlai.scripts.multiprocessing_eval import MultiProcessEval
import light.modeling.loading as load

load.register_all_agents()
load.register_all_tasks()


if __name__ == "__main__":
    MultiProcessEval.main()
