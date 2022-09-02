# CommonSense Turn Based - Crowdsourcing Tasks

This folder contains the 2 tasks used to get human evaluations of our commonsense models, in a "real" text-adventure game environment. Both tasks return the same type of data: annotations of a model's response to an action+context. They also both have the same qualification task, where workers annotate some sample responses for inconsistencies and disfluencies.

We also get error explanations and alternative narrations from these tasks, which could be used to build another dataset.

`live_model_chat` runs one round of a light gameplay (game state selected from a given world-logs) where the worker gives an action, the model responds, and the worker annotates the response

`predetermined_model_chat` is the same as above, but the original worker provided action is set (from previous live chats, for example). Again, the worker annotates the response

The preferred way to use these tasks is to 1) run the `live_model_chat` task with one model to collect a lot of possible context-actions data points, then 2) run `predetermined_model_chat` on that set of context-actions (with multiple workers per unit to get agreement) for every model you want to evaluate.


## How change task setup

To change the data source (game text for `live_model_chat` and context+action for `predetermined_model_chat`) change the `world_log_path` parameter in your yaml file. `world_log_path` should point to a parlai-style jsonl file containing dialogs. To use outputs from `live_model_chat` in `predetermined_model_chat` use the `convert_live_results_to_static.py` script.

To change the model used to produce responses (only relevant for `live_model_chat`) change the `conversations_needed_string` attribute (`model name: {number}` format) in your hydra-configs yaml file and the `model-file` attribute in `task_config/model_opts.yaml`.


## Data exploration

Some preliminary data exploration work is in the `examine_workers.py` files and `calc_agreement.py` in `predetermined_model_chat`.