# LIGHT Common Sense

The goal of the common sense project is to produce models that "understand" our game well enough to produce narrations for the actions users provide. We aim to show that by grounding our models with game graph-modification tasks we improve the quality and consistency of those narrations.

## Structure of codebase

The codebase for this project is split into four pieces across two repos: `LIGHT` (in the `commonsense_v2` branch) and ParlAI-Internal (in the `light_commonsense_v1` branch). Saved files and models should be put in `/checkpoint/light/common_sense/`.

### Data Collection

We have three types of tasks for this project:

`LIGHT/crowdsourcing/custom_world_interactions/`: mephisto tasks to collect use-x-with-y dataset. This data is collected for model training. The README in that folder has more information on how to use.

`LIGHT/crowdsourcing/commonsense_turn_based/`: mephisto tasks to evaluate the narration capabilities of our models. The README in that folder has more information on how to use.

`LIGHT/crowdsourcing/environment/world_builder/`: mephisto world-builder task that uses our grounded models to help workers create new environments. This task still needs to be tested against workers but the README explains the role the common-sense models play and how to switch out model files.

### Teachers

The teachers (and helper files) are in ParlAI-Internal, under `tasks/light_common_sense/`.

### Sweeps

Model sweeps are run from ParlAI-Internal, under `projects/light/common_sense/train_sweeps`. There is also an `old_scripts` folder in `common_sense/` for reference for prior work on graph generation from models.


### Analysis

Scripts to analyse the Use-X-With-Y datasets are here in `./useevent_dataset_scripts/`. The README in that folder has more information on how to use.

Scripts to analyse automated model performance are here in `./model_scripts/`. The README in that folder has more information on how to use.

