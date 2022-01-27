from parlai_internal.projects.param_sweep_utils.param_sweep import run_grid

# 28772546
# SWEEP_NAME = 'sweep_rl_actvalids'
SWEEP_NAME = "sweep_rl_2kquests_2"

NUM_GPUS = 8
name_keys = {}

ks = [-1]
qs = [2000]

qstrs = []

for q in qs:
    cur_str = str(q) + " --k_value " + str(-1)
    qstrs.append(cur_str)
    # qstrs.append(cur_str + ' --flow-encoder --rl_model_file /checkpoint/rajammanabrolu/20200713/sweep_retrieve_multitask_evensmoler/5b1_jobid=1/model')

grid = {
    "--name": [SWEEP_NAME],
    #'--num_processes': [64],
    "--num-quests": qstrs,
    "--log_interval": [10],
    "--run-num": ["0"],
    "--env_model_file": [
        "/checkpoint/rajammanabrolu/20200721/sweep_retrieve_env/_jobid=1/model"
    ],
    #'--switch_steps': [3],
    "--task_type": ["all"],
    "--num_steps": [
        "30 --switch_steps 3 --priority false",
        "100 --switch_steps 6 --priority true",
    ],
    "--enc_type": [
        "text --num_processes 64",
        "largemodelhob --num_processes 16 --rl_model_file /checkpoint/rajammanabrolu/20200721/sweep_retrieve_rl_encoder/_jobid=1/model",
        "largemodelatm --num_processes 16 --rl_model_file /checkpoint/rajammanabrolu/20200701/sweep_retrieve_lightact_multitask_atomic_bert_transfer_lc_fulls/405_jobid=8/model",
    ],
    "--hidden_size": [768],
    "--rewshape": [0.0],
    "--valid-loss-coef": [10],
    "--value-loss-coef": [10],
    "--actor-loss-coef": [1],
    "--entropy-coef": [0.01],
    "--gamma": [0.99],
    "--act_value": [10],
    #'--flow-encoder': ['false']
    #'--recurrent-policy': [True, False],
    #'--k_value': [2, 5, 20, 100]
}

if __name__ == "__main__":
    run_grid(
        grid,
        name_keys,
        SWEEP_NAME,
        partition="learnfair",
        jobtime="72:00:00",
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
