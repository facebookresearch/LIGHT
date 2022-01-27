from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid

# 28140910
SWEEP_NAME = "sweep_rl_curriculum_fixed_rec"
NUM_GPUS = 2
name_keys = {}

ks = [100, 1000]
qs = [500]  # , 20, 100, 500]

curricc = {"linear": [1000, 5000], "reward": [0.5, 2.5]}


qstrs = []

for q in qs:
    for k in ks:
        if k > q:
            cur_str = str(q) + " --k_value " + str(k) + " --recurrent-policy"

            for curriculum, param in curricc.items():
                if curriculum == "linear":
                    for p in param:
                        qstrs.append(
                            cur_str
                            + " --curriculum linear --curr_schedule_steps "
                            + str(p)
                        )
                elif curriculum == "reward":
                    for p in param:
                        qstrs.append(
                            cur_str
                            + " --curriculum reward --curr_rew_threshold "
                            + str(p)
                        )


grid = {
    "--name": [SWEEP_NAME],
    "--num_processes": [32],
    "--num-quests": qstrs,
    "--run-num": ["0"],
    "--curr_step_size": [1, 10]
    #'--rewshape': [0, 0.1, 1]
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
        prefix=". /private/home/rajammanabrolu/.bashrc && python -u parlai_internal/projects/light/quests/tasks/rl_switch/main.py",
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
