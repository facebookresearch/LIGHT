#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Distributed evaluation script. NOT MEANT TO BE CALLED DIRECTLY BY USER.
This script is meant to be in conjunction with
`SLURM <https://slurm.schedmd.com/>`, which provides environmental variables
describing the environment.
An example sbatch script is below, for a 2-host, 8-GPU setup (16 total gpus):
.. code-block:: bash\n\n
  #!/bin/sh
  #SBATCH --job-name=distributed_example
  #SBATCH --output=/path/to/savepoint/stdout.%j
  #SBATCH --error=/path/to/savepoint/stderr.%j
  #SBATCH --partition=priority
  #SBATCH --nodes=2
  #SBATCH --time=0:10:00
  #SBATCH --signal=SIGINT
  #SBATCH --gres=gpu:8
  #SBATCH --ntasks-per-node=8
  #SBATCH --mem=64G
  #SBATCH --cpus-per-task=10
  srun python -u -m parlai.scripts.distributed_eval \
    -m seq2seq -t convai2 --dict-file /path/to/dict-file
"""
import os

import parlai.scripts.eval_model as eval_model
import parlai.utils.distributed as distributed_utils
import light.modeling.loading as load


load.register_all_agents()
load.register_all_tasks()


def main():
    parser = eval_model.setup_args()
    parser.add_distributed_training_args()
    parser.add_argument("--port", type=int, default=61337, help="TCP port number")
    opt = parser.parse_args(print_args=(os.environ["SLURM_PROCID"] == "0"))

    with distributed_utils.slurm_distributed_context(opt) as opt:
        return eval_model.eval_model(opt)


if __name__ == "__main__":
    main()
