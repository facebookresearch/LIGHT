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

from .utils import lev_dist

import os
import json
import shutil
import openai

from typing import Dict, Any, List, Optional

# TARGET_FILE = os.path.join(os.path.dirname(__file__), "out_data", "results.json")
# BACKUP_FILE = TARGET_FILE + ".bak"
TARGET_FILE = os.path.join(os.path.dirname(__file__), "out_data", "no-op-actions.json")
BACKUP_FILE = TARGET_FILE + ".bak"


BASE_OBJECTS_AFTER_PROMPT = """Given context about an interaction between two objects, provide a list of objects that remain in the scene after the action occurs, as well as the reason they are present after the interaction. If a list is empty, enter none. Below are some examples:

Object1: Sewing needle : A sewing needle that is only slightly bent.
Object2: torn fabric : The torn fabric is used as a cloth atop the royal dinner table.
Action: Use the needle to repair the fabric.
Action Description: You use the sewing needle to fix up the rips and tears in the fabric. The fabric looks much less ragged now.
Objects remaining afterwards:
Sewing needle - The needle is unchanged by this interaction, and thus remains in the scene
Repaired fabric - The torn fabric was repaired in the interaction, and thus the torn fabric becomes repaired fabric
Objects no longer present:
Torn fabric - the torn fabric was repaired, and thus is no longer in the scene

Object1: Orange : A juicy orange. It seems to be freshly picked.
Object2: Rusty Broadsword : It's heavy, rusty, and still very sharp. You wouldn't want to be on the pointy side of this one.
Action: slice the orange with the broadsword
Action Description: You cut into the orange with the sword. The weight slices right through, producing two clean orange halves, though you worry a bit about the rust.
Objects remaining afterwards:
Orange halve - the orange was sliced into two halves, this is one of those two halves
Orange halve - the orange was sliced into two halves, this is the other of those two halves
Rusty broadsword - this item is unchanged by this interaction
Objects no longer present:
Orange - the whole orange was sliced, and now is in halves in the scene

Object1: dagger :  a small sharp dagger with an ornate golden handle with carvings.
Object2: door frame : The door frame is made of an old wood with many knicks and scracthes all over it.
Action: Throw dagger at door frame
Action Description: You take aim at the door frame and quickly release the dagger in a skillful forward thrust.  The dagger sticks deep into the door frame among the other knicks and scratches.  The door frame splinters upon impact; your dagger is stuck. 
Objects remaining afterwards:
Dagger - The dagger is stuck in the door frame
Door frame - The door frame is damaged, but remains in the scene
Objects no longer present:
None

Object1: Clogs : Smooth, wooden shoes with a pointed end.
Object2: grapes : The grape is red and juicy and makes you think of summer.
Action: Mash the grapes using the clogs
Action Description: You put on the clogs and repeatedly stomp on the grapes, covering your feet with their crimson liquid.
Objects remaining afterwards:
Mashed grapes - The grapes were mashed in the interaction
Clogs - This item is unchanged by this interaction
Objects no longer present:
Grapes - The grapes were mashed in the interaction

Object1: {} : {}
Object2: {} : {}
Action: {}
Action Description: {}
Objects remaining afterwards:"""


OBJECTS_AFTER_DESCRIPTIONS = """Given context about an interaction between two objects, provide a description for each of the objects present after the interaction. This description should follow even if an observer didn't see the interaction. Below are some examples:

Object1: Metal spoon : A spoon made of metal. Nothing particularly special.
Object2: Vat of bubbling green liquid : This unknown liquid seems dangerous, but you're not sure why.
Action: Stir vat with spoon
Action Description: You stir the green liquid with the spoon. To your surprise, the spoon begins dissolving in your hand as you stir! Shocked, you drop the spoon into the vat. You doubt there's any of it left.
Objects remaining afterwards:
Vat of bubbling green liquid
Descriptions:
Vat of bubbling green liquid: This unknown liquid seems dangerous. You're pretty sure it can dissolve metal, which makes you wonder what the vat itself is made of.

Object1: Wood plank : a wooden plank hewn from an old oak tree 
Object2: saw : this saw will surely be so efficient in cutting a plank.
Action: Cut wood plank with saw
Action Description: You push back and forth with the saw until the wooden plank is cut in half.  You are left with two smaller of wooden planks and a pile of sawdust. 
Objects remaining afterwards:
Two small wooden planks
Saw
Pile of sawdust
Descriptions:
Two small wooden planks: a small wooden plank cut from a larger oak plank.
Saw: this saw will surely be so efficient in cutting a plank.
Pile of sawdust: An ordinary pile of sawdust. Try not to breathe it in!

Object1: Sewing kit : A kit that supplies tools for mending fabrics together.
Object2: torn shirt : The worn shirt looks to have been through a battle, torn and bloody.
Action: Use the sewing kit to repair the torn shirt.
Action Description: Using the sewing kit, you mend the torn shirt back into wearable condition.
Objects remaining afterwards:
Sewing kit
Repaired shirt
Descriptions:
Sewing kit: A kit that supplies tools for mending fabrics together.
Repaired shirt: A shirt that was torn but has been repaired with a sewing kit. It remains bloody though, the sign of a former battle.

Object1: Clogs : Smooth, wooden shoes with a pointed end.
Object2: grapes : The grape is red and juicy and makes you think of summer.
Action: Mash the grapes using the clogs
Action Description: You put on the clogs and repeatedly stomp on the grapes, covering your feet with their crimson liquid.
Objects remaining afterwards:
Mashed grapes
Clogs
Descriptions:
Mashed grapes: Grapes that have been stomped on to become a mushy, red liquid.
Clogs: Smooth, wooden shoes with a pointed end. They are covered in grape juice.

Object1: {} : {}
Object2: {} : {}
Action: {}
Action Description: {}
Objects remaining afterwards:
{}
Descriptions:"""

EXTERNAL_VIEW_PERSPECTIVE_PROMPT = """Given context about an interaction between two objects, provide a narration of the event from the perspective of an onlooker. Ensure not to provide information that the onlooker wouldn't know. Below are some examples:

Object1: Metal spoon : A spoon made of metal. Nothing particularly special.
Object2: Vat of bubbling green liquid : This unknown liquid seems dangerous, but you're not sure why.
Action: Stir vat with spoon
Action Description: You stir the green liquid with the spoon. To your surprise, the spoon begins dissolving in your hand as you stir! Shocked, you drop the spoon into the vat. You doubt there's any of it left.
External Perspective: {{actor}} stirs a vat of green liquid with a spoon. They appear startled, then drop the spoon in entirely!

Object1: Wood plank : a wooden plank hewn from an old oak tree 
Object2: saw : this saw will surely be so efficient in cutting a plank.
Action: Cut wood plank with saw
Action Description: You push back and forth with the saw until the wooden plank is cut in half.  You are left with two smaller of wooden planks and a pile of sawdust. 
External Perspective: {{actor}} saws a wooden plank in half with a saw, leaving behind two smaller planks and some sawdust.

Object1: dagger :  a small sharp dagger with an ornate golden handle with carvings.
Object2: door frame : The door frame is made of an old wood with many knicks and scracthes all over it.
Action: Throw dagger at door frame
Action Description: You take aim at the door frame and quickly release the dagger in a skillful forward thrust.  The dagger sticks deep into the door frame among the other knicks and scratches.  The door frame splinters upon impact; your dagger is stuck. 
External Perspective: {{actor}} skillfully throws a dagger at the door frame. The dagger sticks deep into the door frame, and the door frame splinters.

Object1: Clogs : Smooth, wooden shoes with a pointed end.
Object2: grapes : The grape is red and juicy and makes you think of summer.
Action: Mash the grapes using the clogs
Action Description: You put on the clogs and repeatedly stomp on the grapes, covering your feet with their crimson liquid.
External Perspective: {{actor}} puts on some clogs and repeatedly stomps on some grapes, covering their feet with grape juice.

Object1: {} : {}
Object2: {} : {}
Action: {}
Action Description: {}
External Perspective:"""

FINAL_LOCATION_PROMPT = """Given context about an interaction between two objects and a list of objects remaining in the scene afterwards, provide the locations for each of the remaining objects, as well as a reason for this. Locations should be one of "Held by actor", "worn by actor", "wielded by actor", "in room", the location of one of the original items, or in or on one of the other objects. Below are some examples:

Object1: Metal spoon : A spoon made of metal. Nothing particularly special.
Object2: Vat of bubbling green liquid : This unknown liquid seems dangerous, but you're not sure why.
Action: Stir vat with spoon
Action Description: You stir the green liquid with the spoon. To your surprise, the spoon begins dissolving in your hand as you stir! Shocked, you drop the spoon into the vat. You doubt there's any of it left.
Objects remaining afterwards:
Vat of bubbling liquid
Locations:
Vat of bubbling liquid: nothing in the interaction changes the location of the vat - original location of vat of bubbling green liquid

Object1: Wood plank : a wooden plank hewn from an old oak tree 
Object2: saw : this saw will surely be so efficient in cutting a plank.
Action: Cut wood plank with saw
Action Description: You push back and forth with the saw until the wooden plank is cut in half.  You are left with two smaller of wooden planks and a pile of sawdust. 
Objects remaining afterwards:
Two small wooden planks
Saw
Locations:
Two small wooden planks: the small planks were created from the original wood plank, and should end up in the same location - original location of plank
Saw: nothing in the interaction changes the location of the saw - original location of saw

Object1: Shiny gem : a shiny gem of untold value. You could probably sell this for a pretty penny, or more!
Object2: Coin purse : a small coin purse that can hold a bit of change. It's made of a relatively cheap cloth.
Action: store gem in coin purse
Action Description: You stuff the gem into the coin purse, hoping mostly that it doesn't get scratched by what little change you have in there. Still, it feels safer there than out in the open.
Objects remaining afterwards:
Shiny gem
Coin purse
Locations:
Shiny gem: the actor put the gem into the coin purse - inside coin purse
Coin purse: nothing in the interaction changed the coin purse location - original location of coin purse

Object1: Rock : A small rock with jagged edges found on the ground near a meadow. 
Object2: vultures : The vulture looks a bit hungry, and is eyeing you a bit too closely.  Its feathers are a dark, gloomy shade of black, and its talons look particularly sharp.
Action: throw rock at vultures
Action Description: You throw the rock towards the hungry looking vultures.  It spreads its wings and hops awkwardly backwards observing the rock as it falls to the ground.  The vulture is now angry and approaches menacingly, his sharp talons gripping the ground as with each step.
Objects remaining afterwards:
Rock
Vultures
Locations:
Rock: the rock was thrown by the actor and should wind up on the ground - in room
Vultures: the vultures do not change their location - original location of vultures

Object1: Clogs : Smooth, wooden shoes with a pointed end.
Object2: grapes : The grape is red and juicy and makes you think of summer.
Action: Mash the grapes using the clogs
Action Description: You put on the clogs and repeatedly stomp on the grapes, covering your feet with their crimson liquid.
Objects remaining afterwards:
Mashed grapes
Clogs
Locations:
Mashed grapes: the grapes were mashed by the clogs and should end up where the grapes were - original location of grapes
Clogs: the actor puts on the clogs in order to perform the action - worn by actor


Object1: {} : {}
Object2: {} : {}
Action: {}
Action Description: {}
Objects remaining afterwards:
{}
Locations:"""

RELEVANT_ATTRIBUTE_PROMPT = """You are given context about an interaction between two objects and a list of objects remaining in the scene afterwards. For each of the original objects and for each of the objects in the remaining list, provide a list of attributes that are relevant or required for the interaction to make sense, alongside the reason that attribute is relevant. Include these in Before Attributes and After Attributes sections. Below are some examples:

Object1: Wood plank : a wooden plank hewn from an old oak tree 
Object2: saw : this saw will surely be so efficient in cutting a plank.
Action: Cut wood plank with saw
Action Description: You push back and forth with the saw until the wooden plank is cut in half.  You are left with two smaller of wooden planks and a pile of sawdust. 
Objects remaining afterwards:
Two small wooden planks
Saw
Pile of sawdust
Before Attributes:
Wood plank: wooden - wood is a material that is easily sawed | long - the plank must be long enough to be sawed into two pieces
Saw: sharp - a dull saw wouldn't be easy to use for cutting | thin - the blade of a saw is somewhat thin to make a clean cut
After Attributes:
Two small wooden planks: oak - the original plank was made of oak, so these should be as well
Saw: N/A - there aren't any critical attributes for the saw after the interaction
Pile of sawdust: small - it's unlikely that cutting a single oak plank would make a large pile

Object1: Rock : A small rock with jagged edges found on the ground near a meadow. 
Object2: vultures : The vulture looks a bit hungry, and is eyeing you a bit too closely.  Its feathers are a dark, gloomy shade of black, and its talons look particularly sharp.
Action: throw rock at vultures
Action Description: You throw the rock towards the hungry looking vultures.  It spreads its wings and hops awkwardly backwards observing the rock as it falls to the ground.  The vulture is now angry and approaches menacingly, his sharp talons gripping the ground as with each step.
Objects remaining afterwards:
Rock
Vultures
Before Attributes:
Rock: throwable - the rock must be of a reasonable size to toss
Vultures: attentive - the vulture must be aware of the actor 
After Attributes:
Rock: N/A - there aren't any critical attributes for the rock after the interaction
Vultures: angry - the interaction notes that the vulture was angered by the rock

Object1: Clogs : Smooth, wooden shoes with a pointed end.
Object2: grapes : The grape is red and juicy and makes you think of summer.
Action: Mash the grapes using the clogs
Action Description: You put on the clogs and repeatedly stomp on the grapes, covering your feet with their crimson liquid.
Objects remaining afterwards:
Mashed grapes
Clogs
Before Attributes:
Clogs: hard - the clogs need to be hard to actually crush the grapes | smooth - the clogs should be smooth so as not to damage the grapes
Grapes: red - the color of the grape is relevant to the details in the description | juicy - the grapes must be juicy so that they can be easily mashed
After Attributes:
Mashed grapes: crimson - the grapes are covered in their own juice
Clogs: N/A - there aren't any critical attributes for the clogs after the interaction

Object1: Metal spoon : A spoon made of metal. Nothing particularly special.
Object2: Vat of bubbling green liquid : This unknown liquid seems dangerous, but you're not sure why.
Action: Stir vat with spoon
Action Description: You stir the green liquid with the spoon. To your surprise, the spoon begins dissolving in your hand as you stir! Shocked, you drop the spoon into the vat. You doubt there's any of it left.
Objects remaining afterwards:
Vat of bubbling liquid
Before Attributes:
Metal spoon: stirring - the spoon must be able to mix the liquid | metal - the spoon is made of metal so it will be affected by the liquid
Vat of bubbling liquid: corrosive - the liquid must be corrosive to destroy the metal spoon | green - the color of the liquid is relevant to the details in the description
After Attributes:
Vat of bubbling liquid: N/A - there aren't any critical attributes for the vat after the interaction

Object1: {} : {}
Object2: {} : {}
Action: {}
Action Description: {}
Objects remaining afterwards:
{}
Before Attributes:"""


def get_objects_after_list(example: Dict[str, Any]) -> Dict[str, Any]:
    """prompt for the "objects_afterwards" field"""
    final_prompt = BASE_OBJECTS_AFTER_PROMPT.format(
        example['primary'],
        example['primary_desc'],
        example['secondary'],
        example['secondary_desc'],
        example['raw_action'],
        example['action_desc'],
    )
    subprompt = final_prompt.split('\n\n')[-1]
    completion = openai.Completion.create(
        engine='text-davinci-002', 
        temperature=0.4, # these should be _correct_ answers
        top_p=0.75, # these should be _correct_ answers
        prompt=final_prompt,
        max_tokens=600,
    )
    result = completion.choices[0].text.strip()

    assert len(result.split("Objects no longer present:\n")) == 2, f"Split for objects no longer present is corrupted! {subprompt}{result}"

    remaining_objects_and_reasons, no_longer_present_objects_and_reasons = result.split("Objects no longer present:\n")
    
    remaining_objects_and_reasons = remaining_objects_and_reasons.strip().split("\n")
    remaining_objects = [r_o_r.split(' - ')[0] for r_o_r in remaining_objects_and_reasons]
    remaining_objects = [o for o in remaining_objects if o.lower() != "none" and o.strip() != '']

    no_longer_present_objects_and_reasons = no_longer_present_objects_and_reasons.strip().split("\n")
    not_present_objects = [r_o_r.split(' - ')[0] for r_o_r in no_longer_present_objects_and_reasons]
    not_present_objects = [o for o in not_present_objects if o.lower() != "none" and o.strip() != '']

    full_list = [o.lower() for o in remaining_objects + not_present_objects]
    def is_in_one(val: str):
        for item in full_list:
            if val.lower() in item or item in val.lower():
                return True
        return False
    
    def get_near_match(target: str) -> Optional[str]:
        # Finds the closest match within an edit distance of 4 for the obj and the full list
        for max_dist in [1, 2, 3, 4]:
            for elem in full_list:
                if lev_dist(target, elem) <= max_dist:
                    return elem
        return None

    def replace_in_list(old_val: str, new_val: str):
        for idx, elem in enumerate(remaining_objects):
            if elem == old_val:
                remaining_objects[idx] = new_val
                print(f"{old_val} replaced with {new_val}")
                return
        for idx, elem in enumerate(not_present_objects):
            if elem == old_val:
                not_present_objects[idx] = new_val
                print(f"{old_val} replaced with {new_val}")
                return


    primary_lower = example['primary'].lower()
    if not is_in_one(primary_lower):
        replace_target = get_near_match(primary_lower)
        assert replace_target is not None, f"Primary object not in either remaining or removed list: {subprompt}{result}\n{remaining_objects}"
        replace_in_list(replace_target, primary_lower)
    secondary_lower = example['secondary'].lower()
    if not is_in_one(secondary_lower):
        replace_target = get_near_match(primary_lower)
        assert replace_target is not None, f"Secondary object not in either remaining or removed list: {subprompt}{result}\n{remaining_objects}"
        replace_in_list(replace_target, secondary_lower)

    example['objects_afterwards'] = remaining_objects
    return example


def get_objects_after_descriptions(example: Dict[str, Any]) -> Dict[str, Any]:
    """prompt for the "descriptions_afterwards" field"""
    final_prompt = OBJECTS_AFTER_DESCRIPTIONS.format(
        example['primary'],
        example['primary_desc'],
        example['secondary'],
        example['secondary_desc'],
        example['raw_action'],
        example['action_desc'],
        "\n".join(example['objects_afterwards']),
    )
    subprompt = final_prompt.split('\n\n')[-1]
    completion = openai.Completion.create(
        engine='text-davinci-002', 
        temperature=0.75, # these should be interesting descriptions
        top_p=1,
        prompt=final_prompt,
        max_tokens=500,
    )
    result = completion.choices[0].text.strip()

    item_desc_strings = result.strip().split("\n")
    item_desc_map = {r.split(": ")[0].lower(): ": ".join(r.split(": ")[1:]) for r in item_desc_strings}

    for item in example['objects_afterwards']:
        assert item.lower() in item_desc_map, f"Generated item desc map missing item: {item} - {subprompt}{result}"

    example['descriptions_afterwards'] = item_desc_map
    return example


def get_external_perspective(example: Dict[str, Any]) -> Dict[str, Any]:
    """prompt for the "external_perspective" field"""
    final_prompt = EXTERNAL_VIEW_PERSPECTIVE_PROMPT.format(
        example['primary'],
        example['primary_desc'],
        example['secondary'],
        example['secondary_desc'],
        example['raw_action'],
        example['action_desc'],
    )
    subprompt = final_prompt.split('\n\n')[-1]
    completion = openai.Completion.create(
        engine='text-davinci-002', 
        temperature=0.83, # these should be interesting descriptions
        top_p=1,
        prompt=final_prompt,
        max_tokens=500,
    )
    result = completion.choices[0].text.strip()

    assert "{actor}" in result, f"Description missing {{actor}} entirely, {subprompt}{result}"

    example['external_perspective'] = result
    return example


def get_final_locations(example: Dict[str, Any]) -> Dict[str, Any]:
    """prompt for the "locations_afterwards" field"""
    final_prompt = FINAL_LOCATION_PROMPT.format(
        example['primary'],
        example['primary_desc'],
        example['secondary'],
        example['secondary_desc'],
        example['raw_action'],
        example['action_desc'],
        "\n".join(example['objects_afterwards']),
    )
    subprompt = final_prompt.split('\n\n')[-1]
    completion = openai.Completion.create(
        engine='text-davinci-002', 
        temperature=0.4, # these should be correct answers
        top_p=1, # The valid explanations may be not be the top answers though
        prompt=final_prompt,
        max_tokens=500,
    )
    result = completion.choices[0].text.strip()

    locations_list = result.split('\n')
    location_mapping = {l.split(":")[0].lower(): l.split(" - ")[-1].lower() for l in locations_list}

    possible_targets = [e.lower() for e in example['objects_afterwards']] + [example['primary'].lower(), example['secondary'].lower()]
    def in_possible_targets(target):
        for pos_target in possible_targets:
            if target in pos_target:
                return True
        return False

    for remaining_obj in example['objects_afterwards']:
        assert remaining_obj.lower() in location_mapping, f"Remaining object {remaining_obj} was omitted! {subprompt}{result}"
        location = location_mapping[remaining_obj.lower()]
        target = None
        if location.startswith('original location of '):
            target = location[len('original location of '):]
        elif location.startswith('inside '):
            target = location[len('inside '):]
        if target is not None:
            assert in_possible_targets(target), f"Provided target for {remaining_obj} : {target} was not in {possible_targets} | {subprompt}{result}"

    example['locations_afterwards'] = location_mapping
    return example


def get_relevant_attributes(example: Dict[str, Any]) -> Dict[str, Any]:
    """prompt for the "object_attributes" field"""

    def get_object_attribute_map(attribute_lists: List[str]) -> Dict[str, Dict[str, str]]:
        """Object -> (attribute -> reason)"""
        def get_attribute_reason_map(attribute_list: List[str]) -> Dict[str, str]:
            ret_map = {}
            for attribute in attribute_list:
                if len(attribute.strip()) == 0 or attribute.strip() == "N/A":
                    continue
                attribute_name, attribute_reason = attribute.split(" - ", 1)
                if attribute_name == "N/A" or attribute_name == "":
                    continue
                ret_map[attribute_name] = attribute_reason
            return ret_map
        
        ret_map = {}
        for attribute_string in attribute_lists:
            if attribute_string.strip() == '' or attribute_string.strip() == "N/A":
                continue
            print(attribute_string, attribute_string.split(": "))
            obj_name, obj_attributes = attribute_string.split(": ", 1)
            if obj_name == '':
                continue
            obj_attribute_list = obj_attributes.split(" | ")
            ret_map[obj_name.lower()] = get_attribute_reason_map(obj_attribute_list)

        return ret_map

    final_prompt = RELEVANT_ATTRIBUTE_PROMPT.format(
        example['primary'],
        example['primary_desc'],
        example['secondary'],
        example['secondary_desc'],
        example['raw_action'],
        example['action_desc'],
        "\n".join(example['objects_afterwards']),
    )
    subprompt = final_prompt.split('\n\n')[-1]
    completion = openai.Completion.create(
        engine='text-davinci-002', 
        temperature=0.6, # these should be _generally_ set
        top_p=1,
        prompt=final_prompt,
        max_tokens=800,
    )

    result = completion.choices[0].text.strip()

    assert "After Attributes:\n" in result, f"No split for after objects! in {subprompt}{result}"

    before_attributes, after_attributes = result.split("After Attributes:\n")
    before_attributes = before_attributes.strip().split("\n")
    before_map = get_object_attribute_map(before_attributes)

    def get_near_match(target: str, t_map) -> Optional[str]:
        # Finds the closest match within an edit distance of 4 for the obj and the given map
        for max_dist in [1, 2, 3, 4]:
            for elem in t_map.keys():
                if lev_dist(target, elem) <= max_dist:
                    return elem
        return None

    def replace_in_map(old_val: str, new_val: str, t_map):
        t_map[new_val] = t_map[old_val]
        del t_map[old_val]

    def is_in_map(item, t_map):
        for pos in t_map.keys():
            if item in pos or pos in item:
                return True
        # Try to put into the list
        near_match = get_near_match(item, t_map)
        if near_match is not None:
            replace_in_map(near_match, item, t_map)
            return True
        return False

    for item in [example['primary'].lower(), example['secondary'].lower()]:
        assert is_in_map(item, before_map), f"Before item {item} missing in before attributes {before_map} | {subprompt}{result}"


    after_attributes = after_attributes.strip().split("\n")
    after_map = get_object_attribute_map(after_attributes)
    for item in [e.lower() for e in example['objects_afterwards']]:
        assert is_in_map(item, after_map), f"Before item {item} missing in before attributes {after_map} | {subprompt}{result}"

    example['object_attributes']['before'] = before_map
    example['object_attributes']['after'] = after_map
    return example


def main():
    if os.path.exists(BACKUP_FILE):
        print("Backup file still exists, perhaps something went wrong last run? Check and remove before continuing")
        return
    results = {}
    if os.path.exists(TARGET_FILE):
        shutil.copyfile(TARGET_FILE, BACKUP_FILE)
        with open(TARGET_FILE, 'r') as target_file:
            results = json.load(target_file)

    openai_org_id = input("OpenAI org id: ")
    openai_sk = input("OpenAI API key: ")
    openai.organization = openai_org_id
    openai.api_key = openai_sk

    current_results_len = len(results)
    print("Existing narrations: ", current_results_len)
    current_results_len_json = len(json.dumps(results))

    failed_annotations = 0
    succeeded_annotations = 0
    total_annotations = 0
    for example in list(results.values()):
        try:
            did_something = False
            if example['external_perspective'] is None:
                example = get_external_perspective(example)
                did_something = True
            if example['objects_afterwards'] is None:
                example = get_objects_after_list(example)
                did_something = True
            if example['descriptions_afterwards'] is None:
                example = get_objects_after_descriptions(example)
                did_something = True
            if example['locations_afterwards'] is None:
                example = get_final_locations(example)
                did_something = True
            try:
                if example['object_attributes']['before'] is None:
                    example = get_relevant_attributes(example)
                    did_something = True
            except ValueError:
                did_something = False # We won't count this as successful
                failed_annotations += 1
                pass
            if did_something:
                succeeded_annotations += 1
            total_annotations += 1
        except (AssertionError, openai.error.APIConnectionError, openai.error.Timeout) as e:
            print(e)
            failed_annotations += 1
            pass
        except (BaseException, KeyboardInterrupt) as e:
            print(e)
            import traceback
            traceback.print_exc()
            print("Cleaning up after exception")
            break
        results[example['id']] = example
    
    print(f"{failed_annotations} annotations failed during the annotation process")
    print(f"{succeeded_annotations} are newly completed")
    print(f"{total_annotations} annotations now completed")

    # Write out results
    with open(TARGET_FILE, "w+") as target_file:
        json.dump(results, target_file, indent=2)

    # Before we clear backup, ensure we didn't accidentally delete data
    assert len(results) >= current_results_len
    assert len(json.dumps(results)) >= current_results_len_json
    print("Collected narrations: ", len(results))
    if os.path.exists(BACKUP_FILE):
        os.remove(BACKUP_FILE)

if __name__ == '__main__':
    main()
