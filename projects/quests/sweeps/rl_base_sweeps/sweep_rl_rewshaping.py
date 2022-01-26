from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid

# 28140424 not recurrent
# 28140518 recurrent
SWEEP_NAME = "sweep_rl_rewshape_fixed_1_rec"
NUM_GPUS = 2
name_keys = {}

ks = [100, 1000]
qs = [1, 20, 100, 500]

qstrs = []

for q in qs:
    for k in ks:
        if k > q:
            cur_str = str(q) + " --k_value " + str(k)
            qstrs.append(cur_str + " --recurrent-policy")

grid = {
    "--name": [SWEEP_NAME],
    "--num_processes": [32],
    "--num-quests": qstrs,
    "--run-num": ["0"],
    "--rewshape": [0.0, 0.1, 1.0],
    # '--quest_len': [2]
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
