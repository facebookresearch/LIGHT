#!/usr/bin/env python3
# Builds a LIGHT map using a StarSpace model to connect locations.
# Is not currently connected to the LIGHT text adventure game API
#  (but should be straight-forward).

from parlai.core.params import ParlaiParser
from parlai.core.agents import create_agent
from parlai_internal.projects.light.light_maps.html_map import generate_html_map
from parlai_internal.projects.light.light_maps.filler_rooms import build_filler_rooms
import parlai_internal.projects.light.v1.graph as graph
import pickle
import random
import copy
import numpy as np

random.seed(6)
np.random.seed(6)


def get_random_room(db):
    if "rs" not in db:
        db["rs"] = []
        for r in db["rooms"]:
            db["rs"].append(db["rooms"][r])
    room = random.choice(db["rs"])
    return room


def get_scenario(cdb):
    env = {}
    d = random.choice(cdb)
    env["agents"] = d["agents"]
    env["setting"] = d["setting"]
    # collect actions
    acts = []
    for i in range(0, len(d["character"])):
        if d["emote"][i] is not None:
            acts.append(d["character"][i] + " " + d["emote"][i] + "s")
        if d["action"][i] is not None:
            acts.append(d["character"][i] + " " + d["action"][i])
    env["acts"] = acts
    return env


def go():
    env_file = "/checkpoint/light/light_jfixed_environment.pkl"
    chat_file = "/private/home/jase/src/ParlAI/data/light_dialogue/light_data.pkl"

    print("loading specified db: " + env_file)
    with open(env_file, "rb") as picklefile:
        db = pickle.load(picklefile)
    with open(chat_file, "rb") as picklefile:
        cdb = pickle.load(picklefile)

    while True:
        print("------------------\n")
        scenario = get_scenario(cdb)
        if len(scenario["acts"]) == 0:
            continue

        print("Place: " + scenario["setting"]["name"])

        print("\nCharacters:\n")
        print(
            scenario["agents"][0]["name"].capitalize()
            + " : "
            + scenario["agents"][0]["persona"]
            + "\n"
        )
        print(
            scenario["agents"][1]["name"].capitalize()
            + " : "
            + scenario["agents"][1]["persona"]
            + "\n"
        )

        print("\nThe goal of " + scenario["agents"][0]["name"].capitalize() + " is:")
        print(" ** " + random.choice(scenario["acts"]) + " **\n\n")

        # import pdb; pdb.set_trace()


if __name__ == "__main__":
    random.seed(6)
    go()
