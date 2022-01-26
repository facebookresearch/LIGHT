from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid

# 28153674
SWEEP_NAME = "sweep_rl_valid_curric"
NUM_GPUS = 2
name_keys = {}

ks = [-1]
qs = [500]

curricc = {"reward": [1, 2.5, 5]}


qstrs = []

for q in qs:
    cur_str = str(q) + " --recurrent-policy"

    for curriculum, param in curricc.items():
        if curriculum == "linear":
            for p in param:
                qstrs.append(
                    cur_str + " --curriculum linear --curr_schedule_steps " + str(p)
                )
        elif curriculum == "reward":
            for p in param:
                qstrs.append(
                    cur_str + " --curriculum reward --curr_rew_threshold " + str(p)
                )
        elif curriculum == "none":
            qstrs.append(cur_str)

grid = {
    "--name": [SWEEP_NAME],
    "--num_processes": [32],
    "--num-quests": qstrs,
    "--run-num": ["0"],
    "--curr_step_size": [1],
    "--rewshape": [1],
    "--valid-loss-coef": [10],
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
