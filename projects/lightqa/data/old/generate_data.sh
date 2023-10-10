#!/bin/bash
## Run with: sbatch generate_data.sh
### Section1: SBATCH directives to specify job configuration

## job name
#SBATCH --job-name=generate_data

## partition name
#SBATCH --partition=learnfair
## number of nodes
#SBATCH --nodes=1

## number of tasks per node
#SBATCH --ntasks-per-node=8
#SBATCH --gpus-per-node=8
#SBATCH --cpus-per-task=10
#SBATCH --time=220

### Section 2: Setting environment variables for the job
### Remember that all the module command does is set environment
### variables for the software you need to. Here I am assuming I
### going to run something with python.
### You can also set additional environment variables here and
### SLURM will capture all of them for each task
# Start clean
module purge


module load anaconda3
source activate py38

srun --label python3 generate_data.py --datatype valid
