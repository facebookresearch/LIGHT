# LIGHT

![Python test](https://github.com/facebookresearch/LIGHT/workflows/Python%20test/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier)

This directory is home to the [LIGHT](https://parl.ai/projects/light/) project. At the moment it is very much a migration in progress, but it will be home to all of the LIGHT experiments, reproducible code, and more! For now, much of the code is split between the two locations, so missing segments and data can likely be found from the projects game.

## What is LIGHT?

LIGHT is part Text-Adventure game, part Dialogue + Natural Language research platform. We host a game at [light-rpg.ai](https://light-rpg.ai) built upon the research work contained in this repo. Here we're also happy to consider developments from the LIGHT community of researchers, creators, and players. Our long-term goal is to create something that is all of:
1. A strong multiplayer game environment that is easy and fun to interact with for players.
2. An AI-Powered storytelling tool for creators to build interactive experiences for others to enjoy.
3. A platform for exploring advancements in Dialogue and Natural Language research through developing better models to power the game.

## The LIGHT Repo

This repo contains a few directories related to the LIGHT project. More details can be found in each directory:
- [**`crowdsourcing`**](https://github.com/facebookresearch/LIGHT/tree/main/crowdsourcing): Contains the full setup and deploy code for (nearly) all of the crowdsourced data used in LIGHT. Useful examples of how to collect similar types of data.
- [**`deploy`**](https://github.com/facebookresearch/LIGHT/tree/main/deploy): Contains code relevant for various deploys of LIGHT for public consumption.
- [**`light`**](https://github.com/facebookresearch/LIGHT/tree/main/light): Contains the core LIGHT game engine, modeling, and tasks. The core includes the `OOGraph` data model, descriptions of all of the node types, actions and manipulations on the graph (`GraphEvent`s), and the abstract API (`Soul`s) for creating agents that can act in LIGHT.
- [**`projects`**](https://github.com/facebookresearch/LIGHT/tree/main/projects): Contains code that's still in-development, either for research endeavors that haven't yet been incorporated into the game, or works that derive from work but ultimately don't feed back in. Also contains code relevant preserved to reproduce specific paper results.
- [**`scripts`**](https://github.com/facebookresearch/LIGHT/tree/main/scripts): Contains execution code for running LIGHT, exploring our dataset, filtering through examples, and more.

## Getting started

First off, to get started you'll need to install LIGHT into your python environment. For this, you can navigate to this repo and run
```
pip install -e .
```
The rest of the core interactions with LIGHT may require additional environment and other downloads, explained below.

### Interacting with the LIGHT engine (no models)
To jump right into a LIGHT world on the command line, you can use some of our example code. The following will put you in the simplest world:
```
python scripts/examples/play_map.py
```

You can also try a more complex LIGHT world using the following:
```
python scripts/examples/play_map.py --load-map scripts/examples/complex_world.json
```

Deeper explanations on how the engine itself functions can be found in the [LIGHT graph](https://github.com/facebookresearch/LIGHT/tree/main/light/graph) directory.

### Exploring the environment with models

TODO - Fill out once all of the required minimal models are hosted for access outside of the cluster.

### Launching the full game server locally

TODO - more details are in the [web deploy](https://github.com/facebookresearch/LIGHT/tree/main/deploy/web/) directory.

## Creating tasks and agents
We use the "register" syntax so that new agents and tasks are visible to the parlai module. Note, however,
that in any script that uses these tasks or agents, you will have to make a call to the functions `register_all_agents()` and `register_all_tasks()` which can be found in `light/modeling/loading.py`.

**ALTERNATIVELY** you can consider using the supercommand: `light`. The following commands accomplish the same thing:

- `python scripts/train_model.py` and `light tm`
- `python scripts/display_data.py` and `light dd`
- `python scripts/eval_model.py` and `light em`
- etc.

Using `light` will automatically load the correct modules from inside this repo so that they are visible to ParlAI.

## License
LIGHT is MIT licensed. See the **[LICENSE](https://github.com/facebookresearch/LIGHT/blob/main/LICENSE)** file for details.
