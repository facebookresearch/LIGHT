from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid

# 28171564
SWEEP_NAME = "sweep_rl_flow_valid"
NUM_GPUS = 2
name_keys = {}

ks = [-1]
qs = [1, 100, 500]

qstrs = []

for q in qs:
    cur_str = str(q) + " --k_value " + str(-1)
    qstrs.append(cur_str)
    qstrs.append(cur_str + " --flow-encoder")

grid = {
    "--name": [SWEEP_NAME],
    "--num_processes": [32],
    "--num-quests": qstrs,
    "--run-num": ["0"],
    "--rewshape": [0.0, 1.0],
    "--valid-loss-coef": [1, 5, 10]
    #'--recurrent-policy': [True, False],
    #'--k_value': [2, 5, 20, 100]
}

if __name__ == "__main__":
    run_grid(
        grid,
        name_keys,
        SWEEP_NAME,
        partition="learnfair",
        jobtime="48:00:00",
        prefix=". /private/home/rajammanabrolu/.bashrc && python -u parlai_internal/projects/light/quests/tasks/rl_base/main.py",
        PARLAI_PATH="/private/home/rajammanabrolu/ParlAI/",
        cpus=20,
        gpus=NUM_GPUS,
        nodes=1,
        volta32=True,
        create_model_file=False,
        data_parallel=True,
        include_job_id=True,
        requeue=True,
        copy_env=False,
    )
