# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3
import argparse
import torch
from light.constants import LIGHT_DATAPATH


def get_args():
    parser = argparse.ArgumentParser(description="RL")

    ## Light arguments
    parser.add_argument("--light_use_setting", type=bool, default=True)
    parser.add_argument("--light_use_person_names", type=bool, default=True)
    parser.add_argument(
        "--light_use_persona",
        type=str,
        default="all",
        choices=["partner", "self", "all", "none"],
    )
    parser.add_argument("--light_use_objects", type=bool, default=False)
    parser.add_argument("--light_use_emote_goals", type=bool, default=False)

    parser.add_argument("--goal_types", type=str, default="action")

    parser.add_argument(
        "--save_interval",
        type=int,
        default=100,
    )
    parser.add_argument(
        "--log_interval",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--name",
        type=str,
        default="sanity_rst1",
    )
    parser.add_argument(
        "--run-num",
        type=str,
        default="0",
    )

    parser.add_argument(
        "--speech_fixed_candidate_file",
        type=str,
        default="quest_speech_cands.txt",  # TODO replace with LIGHT path after finishing format
    )
    parser.add_argument(
        "--quest_all_cands",
        type=str,
        default="quest_all_cands.txt",  # TODO replace with LIGHT path after finishing format
    )
    parser.add_argument(
        "--env_all_cands",
        type=str,
        default="env_all_cands.txt",  # TODO replace with LIGHT path after finishing format
    )
    parser.add_argument(
        "--env_act_cands",
        type=str,
        default="env_act_cands.txt",  # TODO replace with LIGHT path after finishing format
    )
    parser.add_argument(
        "--act_fixed_candidate_file",
        type=str,
        default="quest_act_cands.txt",  # TODO replace with LIGHT path after finishing format
    )

    parser.add_argument(
        "--rl_model_file",
        type=str,
        # kitchen sink large polyencoder
        # default=os.path.join(LIGHT_DATAPATH, "quests/rl_quests_resources/base_models/kitchen_sink/model"),
        # hobbot large polyencoder
        # default=os.path.join(LIGHT_DATAPATH, "quests/rl_quests_resources/wild_large_poly/kitchen_sink/model"),
        # untrained small polyencoder
        default=os.path.join(
            LIGHT_DATAPATH,
            "quests/rl_quests_resources/base_models/untrained_small_poly/model",
        ),
    )
    parser.add_argument(
        "--flow-encoder",
        default="false",
        help="freeze RL encoders or not",
    )
    parser.add_argument(
        "--env_model_file",
        type=str,
        default=os.path.join(
            LIGHT_DATAPATH, "quests/rl_quests_resources/env_model/model"
        ),
    )

    parser.add_argument(
        "--dm_model_file",
        type=str,
        default=os.path.join(
            LIGHT_DATAPATH, "quests/rl_quests_resources/dm_model/model"
        ),
    )
    parser.add_argument(
        "--data_file",
        type=str,  # TODO update data file to json rather than .pkl, replace with quests/wild_chats/formatted_wild_completions.json
        default=os.path.join(
            LIGHT_DATAPATH, "quests/wild_chats/formatted_wild_completions.json"
        ),
    )
    parser.add_argument("--fixed_episodes_file", type=str, default=None)
    parser.add_argument("--shuffle_episodes", type=bool, default=False)
    parser.add_argument(
        "--write_reward_file",
        type=str,
        default=os.path.join(LIGHT_DATAPATH, "out/quests/action_rewards.csv"),
    )
    parser.add_argument(
        "--save_dir",
        type=str,
        default=os.path.join(LIGHT_DATAPATH, "out/quests/rl_switch/logs"),
    )
    parser.add_argument(
        "--model_dir",
        type=str,
        default=os.path.join(LIGHT_DATAPATH, "out/quests/rl_switch/models"),
    )
    parser.add_argument(
        "--combo",
        default="train_ex",
        help="what to train on: "
        "train_ex | formatted_hobbot_quests_trainall | mix | achievable",
    )

    parser.add_argument(
        "--model_type",
        default="topk",
        help="model architecture to train/eval: cluster | topk | inverse | topkbiencoder",
    )

    parser.add_argument(
        "--priority",
        default="false",
        help="Use quest priority sampling or not, true/false",
    )

    parser.add_argument(
        "--num_clusters",
        type=int,
        default=50,
        help="number of clusters in cluster setup",
    )
    parser.add_argument("--eval_mode", type=str, default="train")
    parser.add_argument("--max_eval_eps", type=int, default=-1)
    parser.add_argument("--write_eval_eps", type=bool, default=False)
    parser.add_argument(
        "--write_results_dir",
        type=str,
        default=os.path.join(LIGHT_DATAPATH, "out/quests/rl_switch/results"),
    )
    parser.add_argument("--write_results_file", type=str, default=None)

    parser.add_argument(
        "--train_from",
        type=str,
        default="",
        help="If you want to continue training from a checkpoint.",
    )
    parser.add_argument("--block_repeats", type=bool, default=True)
    parser.add_argument("--use_kfac_optim", type=bool, default=False)

    parser.add_argument("--use_adam", type=bool, default=True)

    parser.add_argument("--normalize_rl_input", type=bool, default=False)
    parser.add_argument("--no_stopwords", type=bool, default=False)
    parser.add_argument("--utt_reward_threshold_start", type=float, default=0.2)
    parser.add_argument("--write_test_episodes_file", type=str, default=None)
    parser.add_argument(
        "--episode_steps",
        type=int,
        default=None,
        help="number of steps in each episode",
    )

    parser.add_argument(
        "--algo", default="a2c", help="algorithm to use: a2c | ppo | acktr"
    )
    parser.add_argument(
        "--algo_mode",
        default="train",
        help="algorithm mode to use: train | test | inverse",
    )
    parser.add_argument(
        "--gail",
        action="store_true",
        default=False,
        help="do imitation learning with gail",
    )
    parser.add_argument(
        "--gail-experts-dir",
        default="./gail_experts",
        help="directory that contains expert demonstrations for gail",
    )
    parser.add_argument(
        "--gail-batch-size",
        type=int,
        default=128,
        help="gail batch size (default: 128)",
    )
    parser.add_argument(
        "--gail-epoch", type=int, default=5, help="gail epochs (default: 5)"
    )
    parser.add_argument(
        "--lr", type=float, default=0.0003, help="learning rate (default: 7e-4)"
    )
    parser.add_argument(
        "--eps",
        type=float,
        default=1e-8,
        help="RMSprop optimizer epsilon (default: 1e-5)",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.99,
        help="RMSprop optimizer alpha (default: 0.99)",
    )
    parser.add_argument(
        "--gamma",
        type=float,
        default=0.99,
        help="discount factor for rewards (default: 0.99)",
    )
    parser.add_argument(
        "--use-gae",
        action="store_true",
        default=False,
        help="use generalized advantage estimation",
    )
    parser.add_argument(
        "--gae-lambda",
        type=float,
        default=0.95,
        help="gae lambda parameter (default: 0.95)",
    )
    parser.add_argument(
        "--entropy-coef",
        type=float,
        default=0.00,
        help="entropy term coefficient (default: 0.01)",
    )
    parser.add_argument(
        "--value-loss-coef",
        type=float,
        default=10,
        help="value loss coefficient (default: 10)",
    )
    parser.add_argument(
        "--valid-loss-coef",
        type=float,
        default=10,
        help="Valid loss coefficient (default: 10)",
    )
    parser.add_argument(
        "--actor-loss-coef",
        type=float,
        default=1,
        help="Policy loss coefficient (default: 1)",
    )
    parser.add_argument(
        "--scale-coef",
        type=float,
        default=4,
        help="Extra multiplier for speech",
    )
    parser.add_argument(
        "--max-grad-norm",
        type=float,
        default=40,
        help="max norm of gradients (default: 0.5)",
    )
    parser.add_argument(
        "--seed", type=int, default=19, help="random seed (default: 19)"
    )
    parser.add_argument(
        "--cuda-deterministic",
        action="store_true",
        default=False,
        help="sets flags for determinism when using CUDA (potentially slow!)",
    )
    parser.add_argument(
        "--ppo-epoch", type=int, default=4, help="number of ppo epochs (default: 4)"
    )
    parser.add_argument(
        "--num-mini-batch",
        type=int,
        default=4,
        help="number of batches for ppo (default: 32)",
    )
    parser.add_argument(
        "--clip-param",
        type=float,
        default=0.2,
        help="ppo clip parameter (default: 0.2)",
    )
    parser.add_argument(
        "--eval-interval",
        type=int,
        default=None,
        help="eval interval, one eval per n updates (default: None)",
    )
    parser.add_argument(
        "--num-env-steps",
        type=int,
        default=10e6,
        help="number of environment steps to train (default: 10e6)",
    )
    parser.add_argument(
        "--env-name",
        default="light_rl.v1.93",
        help="environment to train on (default: PongNoFrameskip-v4)",
    )
    parser.add_argument(
        "--log-dir",
        default="/tmp/seed93",
        help="directory to save agent logs (default: /tmp/gym)",
    )
    parser.add_argument(
        "--no-cuda", action="store_true", default=False, help="disables CUDA training"
    )
    parser.add_argument(
        "--use-proper-time-limits",
        action="store_true",
        default=False,
        help="compute returns taking into account time limits",
    )
    parser.add_argument(
        "--enc_type",
        type=str,
        default="text",
    )
    parser.add_argument(
        "--task_type",
        type=str,
        default="all",
    )
    parser.add_argument(
        "--droptask",
        type=str,
        default="0.0,0.0,1.0",
    )
    parser.add_argument(
        "--dropint",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--num-quests",
        type=int,
        default=4,
    )
    parser.add_argument(
        "--num_steps",
        type=int,
        default=30,
        help="number of forward steps in A2C (default: 10)",
    )
    parser.add_argument(
        "--switch_steps",
        type=int,
        default=3,
        help="number of steps after RL agent acts",
    )
    parser.add_argument(
        "--hidden_size",
        type=int,
        default=768,
        help="intermediate node sizes",
    )
    parser.add_argument(
        "--k_value",
        type=int,
        default=-1,
        help="number of candidates to use for top k, -1 to use all",
    )
    parser.add_argument(
        "--act_value",
        type=int,
        default=10,
        help="number of candidates to use for valid masking",
    )
    parser.add_argument(
        "--dm",
        action="store_true",
        default=False,
        help="use stars as speech reward",
    )
    parser.add_argument(
        "--num_processes",
        type=int,
        default=4,
        help="how many training CPU processes to use (default: 16)",
    )
    parser.add_argument(
        "--quest_len",
        type=int,
        default=1,
        help="Quest min length",
    )
    parser.add_argument(
        "--rewshape",
        type=float,
        default=0.0,
        help="Rewards for intermediate quest steps",
    )
    parser.add_argument(
        "--recurrent-policy",
        action="store_true",
        default=True,
        help="use a recurrent policy",
    )
    parser.add_argument(
        "--curriculum",
        type=str,
        default="none",
        help="use curriculum: types none, linear, reward",
    )
    parser.add_argument(
        "--curr_step_size",
        type=int,
        default=4,
        help="How many quests to increment the pool by each time",
    )
    parser.add_argument(
        "--curr_schedule_steps",
        type=int,
        default=1000,
        help="Use with linear schedule, increment pool after n updates",
    )
    parser.add_argument(
        "--curr_rew_threshold",
        type=float,
        default=1.0,
        help="Use with reward schedule, increment pool after with greater than x avg episode rews",
    )
    parser.add_argument(
        "--use-linear-lr-decay",
        action="store_true",
        default=False,
        help="use a linear schedule on the learning rate",
    )
    args = parser.parse_args()
    args = vars(args)

    args["cuda"] = not args["no_cuda"] and torch.cuda.is_available()

    # if args['curriculum'] is not 'none':
    #    args['num_quests'] = 500

    assert args["algo"] in ["a2c", "ppo", "acktr"]
    if args["recurrent_policy"]:
        assert args["algo"] in [
            "a2c",
            "ppo",
        ], "Recurrent policy is not implemented for ACKTR"

    name_keys = [
        "name",
        "num_quests",
        "k_value",
        "droptask",
        "dropint",
        "rewshape",
        "task_type",
        "enc_type",
        "priority",
        "switch_steps",
        "num_steps",
        "flow_encoder",
        "act_value",
        "scale_coef",
    ]
    allfname = ""
    for key in name_keys:
        allfname += "_" + key.split("_")[0] + "_" + str(args[key])
    args["allfname"] = allfname[1:]
    return args
