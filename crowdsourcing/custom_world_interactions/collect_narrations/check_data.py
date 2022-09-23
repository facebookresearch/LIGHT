#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Given data (already in the results file), run a few queries against GPT to
populate initial values for the potential grounding.
"""

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.agent import AgentState

import os
import json
import shutil
import openai

from typing import Dict, Any, List, Optional

TARGET_FILE = os.path.join(os.path.dirname(__file__), "out_data", "results.json")
BACKUP_FILE = TARGET_FILE + ".bak"


OBJECT_CARRYABLE_PROMPT = """Given an object, determine if it can be carried by hand. Here are some examples:

Object: Sewing needle : A sewing needle that is only slightly bent.
You can carry the sewing needle

Object: torn fabric : The torn fabric is used as a cloth atop the royal dinner table.
You can carry the torn fabric

Object: door frame : The door frame is made of an old wood with many nicks and scratches all over it.
You can't carry the door frame

Object: dagger :  a small sharp dagger with an ornate golden handle with carvings.
You can carry the dagger

Object: statue: A life-size statue of the king. It looks kind of silly though.
You can't carry the statue

Object: chisel: A run-of-the-mill stone carving tool. Still dusty from its last use.
You can carry the chisel

Object: boulder: This boulder is massive, and you doubt it can ever be moved.
You can't carry the boulder

Object: house: A small family home, with four glass windows you can peer into.
You can't carry the house

Object: statue: A small statue you might see in a souvenir shop.
You can carry the statue

Object: magic boulder : A boulder that's enchanted with the power of air. It's light as a feather!
You can carry the magic boulder

Object: Spear : A six foot wooden spear with a sharp metal point on one end.
You can carry the spear

Object: Sword : the sword is sharp and heavy, decorated with patterns of dragons and tigers.
You can carry the sword

Object: net : A large net that has the ability to catch objects in it.
You can carry the net

Object: lit torch : The torch has fire and is not safe around flammable things.
You can carry the lit torch

Object: {} : {}
"""


CONTEXT_EXPLAINED_PROMPT = """Given two objects, determine if a description of an action involving the two is relying on context outside of the objects and their descriptions. Pay attention to mentions of locations, as the interactions shouldn't specify the place they occur in. Interactions also shouldn't assume anything about the actor.

Object: Metal spoon : A spoon made of metal. Nothing particularly special.
Object: Vat of bubbling green liquid : This unknown liquid seems dangerous, but you're not sure why.
Action: You stir the green liquid with the spoon. To your surprise, the spoon begins dissolving in your hand as you stir! Shocked, you drop the spoon into the vat. You doubt there's any of it left.
Is everything in the action explained by the objects? Yes - All referred to context is present in the object descriptions.

Object: Engraving knife : Sharp and small the engraving knife can add character to any object
Object: food tray : A simple tray, to put one's food on.
Action: You cut into the tray with the engraving knife, creating swirling patterns on its plain surface. In the end, it is so much prettier, and your wife is so happy for it, she tells everyone in the kingdom.
Is everything in the action explained by the objects? No - Not all context is present. The action description refers to your wife, but nothing about the objects implies she exists.

Object: Wood plank : a wooden plank hewn from an old oak tree 
Object: saw : this saw will surely be so efficient in cutting a plank.
Action: You push back and forth with the saw until the wooden plank is cut in half.  You are left with two smaller of wooden planks and a pile of sawdust. 
Is everything in the action explained by the objects? Yes - All referred to context is present in the object descriptions.

Object: door : A creaky wooden door on rusty hinges.
Object: table : Dented, chipped, and leaning slightly to the side, this table is a witness to many brawls.
Action: You run inside the room and quickly close the wooden door, but know that it is not strong enough to keep the others out. You push the table towards the door to create a barricade. Hopefully it will hold.
Is everything in the action explained by the objects? No - Not all context is present. Nothing about the objects forces you to run into the room, and nothing else refers to "the others".

Object: torch : A handle held wooden torch
Object: tattered tunic : The tattered tunic is in such poor condition that you can barely make out the original shape of the tunic.
Action: You see an old tattered tunic in the corner of the dark temple and light it on fire with your torch. As the tunic catches fire, it begins to shed more light and brightens the room.
Is everything in the action explained by the objects? No - Not all context is present. Nothing about the objects implies that the tunic is in the corner of a dark temple.

Object: Clogs : Smooth, wooden shoes with a pointed end.
Object: grapes : The grape is red and juicy and makes you think of summer.
Action Description: You put on the clogs and repeatedly stomp on the grapes, covering your feet with their crimson liquid.
Is everything in the action explained by the objects? Yes - All referred to context is present in the object descriptions.

Object: Shield : A metal shield that is highly polished and brightly reflects light.
Object: little wooden stool : The little wooden stool is worn and battered from use.
Action: You are tired after traveling for days and can't wait to finally rest. You place your prized shield upon a small wooden stool before sitting at the long table for a meal.
Is everything in the action explained by the objects? No - Not all context is present. Nothing in the objects implies that you have been traveling for days.

Object: Spell book : An ancient book of spells that hums with magical energies.
Object: cape : A tattered cape, riddled with rips and tears.
Action: You realize the spell book must be taken from the dark keep and handled with care. You remove your old tattered cape from your back and wrap it around the book before placing in your pack. You can still hear it humming from inside the cape.
Is everything in the action explained by the objects? No - Not all context is present. The action description refers to a dark keep, but nothing about the objects implies that it exists. 

Object: Sewing kit : A kit that supplies tools for mending fabrics together.
Object: torn shirt : The worn shirt looks to have been through a battle, torn and bloody.
Action: Using the sewing kit, you mend the torn shirt back into wearable condition.
Is everything in the action explained by the objects? Yes - All referred to context is present in the object descriptions.

Object: {} : {}
Object: {} : {}
Action: {}
Is everything in the action explained by the objects?"""

def determine_objects_holdable(example: Dict[str, Any]) -> Dict[str, Any]:
    """prompt for the "_carryable" fields"""
    final_prompt = OBJECT_CARRYABLE_PROMPT.format(
        example['primary'],
        example['primary_desc'],
    )
    completion = openai.Completion.create(
        engine='text-davinci-002', 
        temperature=0.3, # these should be _correct_ answers
        top_p=0.75, # these should be _correct_ answers
        prompt=final_prompt,
        max_tokens=30,
    )
    example['primary_carryable'] = "can't" not in completion.choices[0].text.strip()

    final_prompt = OBJECT_CARRYABLE_PROMPT.format(
        example['secondary'],
        example['secondary_desc'],
    )
    completion = openai.Completion.create(
        engine='text-davinci-002', 
        temperature=0.3, # these should be _correct_ answers
        top_p=0.75, # these should be _correct_ answers
        prompt=final_prompt,
        max_tokens=30,
    )

    example['secondary_carryable'] = "can't" not in completion.choices[0].text.strip()
    return example


def determine_context(example: Dict[str, Any]) -> Dict[str, Any]:
    """prompt for the "descriptions_afterwards" field"""
    final_prompt = CONTEXT_EXPLAINED_PROMPT.format(
        example['primary'],
        example['primary_desc'],
        example['secondary'],
        example['secondary_desc'],
        example['action_desc'],
    )
    completion = openai.Completion.create(
        engine='text-davinci-002', 
        temperature=0.75, # these should be interesting descriptions
        top_p=1,
        prompt=final_prompt,
        max_tokens=200,
    )
    result = completion.choices[0].text.strip()

    example['context_consistent'] = result
    return example


def main():
    target_filename = os.path.join('out_data', input('target filename (from out_data folder): '))
    backup_filename = target_filename + ".bak"
    if os.path.exists(backup_filename):
        print("Backup file still exists, perhaps something went wrong last run? Check and remove before continuing")
        return
    results = {}
    if os.path.exists(target_filename):
        shutil.copyfile(target_filename, backup_filename)
        with open(target_filename, 'r') as target_file:
            results = json.load(target_file)

    openai_org_id = input("OpenAI org id: ")
    openai_sk = input("OpenAI API key: ")
    openai.organization = openai_org_id
    openai.api_key = openai_sk

    input(f"Run check on up to {len(results)} results?")

    try:
        for example in list(results.values()):
            try:
                if example.get('primary_carryable') is None:
                    example = determine_objects_holdable(example)
                if example.get('context_consistent') is None:
                    example = determine_context(example)
            except openai.error.ServiceUnavailableError as _e:
                import time
                time.sleep(1)
            except AssertionError as e:
                print(e)
                pass
            results[example['id']] = example
    except:
        pass
    
    # Write out results
    with open(target_filename, "w+") as target_file:
        json.dump(results, target_file, indent=2)

    # Before we clear backup, ensure we didn't accidentally delete data
    if os.path.exists(backup_filename):
        os.remove(backup_filename)

if __name__ == '__main__':
    main()