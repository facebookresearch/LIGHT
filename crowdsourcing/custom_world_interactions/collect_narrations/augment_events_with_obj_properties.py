import os
import time
import openai
import random
from functools import wraps
from light.data_model.db.environment import EnvDB
from light.data_model.db.base import LightLocalDBConfig

from typing import Dict, Any, List, Optional, Tuple, TYPE_CHECKING


EVENTS_OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "out_data", "events.json")
LIGHT_DB_PATH = "/checkpoint/light/db/prod"

# This query can take an object and their relevant character and provide a description and attributes
OBJECT_ANNOTATION = """Given a an object name and physical description from a medieval fantasy text adventure, provide values for the specific attributes below. For example:
Name: sword
Description: This sword is sharp and heavy, and could likely do a lot of damage if swung. Don't swing it at anything important!
Food: no
Drink: no
Holdable: yes
Wearable: no
Wieldable: yes
Surface: no
Container: no

Name: {}
Description: {}
Food:"""

last_query = None
def query_openai(
    prompt: str,
    temperature: float = 0.7,
    top_p: float = 1.0,
    frequency_penalty: float = 0,
    presence_penalty: float = 0,
):
    """Wrapper around openai queries, with some parameters"""
    global last_query
    completion = openai.Completion.create(
        engine="text-davinci-002",
        temperature=temperature,
        top_p=top_p,
        prompt=prompt,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        max_tokens=700,
    )
    last_query = f"Prompt: {prompt}\nGeneration: {completion.choices[0].text.strip()}"
    print(".", end="", flush=True)
    return completion.choices[0].text.strip()


def retry(count=5, exc_type=Exception):
    def decorator(func):
        @wraps(func)
        def result(*args, **kwargs):
            ret_exec = None
            for _i in range(count):
                try:
                    return func(*args, **kwargs)
                except exc_type as e:
                    ret_exec = e
                    print("e", end="", flush=True)
            print("Exception Query:\n" + last_query)
            raise ret_exec

        return result

    return decorator


@retry(count=8)
def annotate_object(
    object_name: str, object_desc: str,
) -> Dict[str, List[str]]:
    """Given an object name, annotate it fully"""
    final_prompt = OBJECT_ANNOTATION.format(object_name, object_desc)
    result = query_openai(final_prompt)
    if "Name:" in result:
        result = result.split("Name:")[0]

    is_food, other = result.split("\nDrink:")
    is_drink, other = other.split("\nHoldable:")
    is_holdable, other = other.split("\nWearable:")
    is_wearable, other = other.split("\nWieldable:")
    is_wieldable, other = other.split("\nSurface:")
    is_surface, is_container = other.split("\nContainer:")
    return {
        "is_food": is_food.strip() == "yes",
        "is_drink": is_drink.strip() == "yes",
        "is_holdable": is_holdable.strip() == "yes",
        "is_wearable": is_wearable.strip() == "yes",
        "is_wieldable": is_wieldable.strip() == "yes",
        "is_surface": is_surface.strip() == "yes",
        "is_container": is_container.strip() == "yes",
    }


if __name__ == '__main__':
    import os
    import json
    from light.dirs import LIGHT_DIR

    backend = 'openai'

    org_id = input("Provide openai Org ID: ")
    openai_sk = input("Provide openai Secret Key: ")
    
    openai.organization = org_id
    openai.api_key = openai_sk

    ldb = EnvDB(LightLocalDBConfig(file_root=LIGHT_DB_PATH))

    with open(EVENTS_OUTPUT_FILE, 'r') as json_file:
        events = json.load(json_file)

    all_events = events['unseen'] + events['train'] + events['valid'] + events['test']

    tot_events = 0
    tot_objs = 0
    db_objs = 0
    done_objs = 0
    queried_objs = 0
    cached_objs = {}
    annotated_objs = {}
    for event in all_events:
        try:
            all_objs = [event['obj1'], event['obj2']] + [
                o for o in event['objects_afterwards'] 
                if o['change'] == 'ADDED'
            ]
            tot_events += 1
            for obj in all_objs:
                tot_objs += 1
                if obj.get('is_food') != None:
                    obj['name'] = obj['name'].strip()
                    obj['desc'] = obj['desc'].strip()
                    done_objs += 1
                    continue
                found_obj = cached_objs.get((obj['name'], obj['desc']))
                if found_obj is not None:
                    found_objs = [found_obj]
                else:
                    found_objs = ldb.find_objects(name=obj['name'], physical_description=obj['desc'])
                if len(found_objs) > 0:
                    db_obj = found_objs[0]
                    cached_objs[(obj['name'], obj['desc'])] = db_obj
                    obj.update({
                        "is_food": db_obj.is_food > 0.5,
                        "is_drink": db_obj.is_drink > 0.5,
                        "is_holdable": db_obj.is_gettable > 0.5,
                        "is_wearable": db_obj.is_wearable > 0.5,
                        "is_wieldable": db_obj.is_weapon > 0.5,
                        "is_surface": db_obj.is_surface > 0.5,
                        "is_container": db_obj.is_container > 0.5,
                    })
                    db_objs += 1
                else:
                    annotated_obj = annotated_objs.get((obj['name'], obj['desc']))
                    if annotated_obj is None:
                        annotated_obj = annotate_object(obj['name'], obj['desc'])
                    annotated_objs[(obj['name'], obj['desc'])] = annotated_obj
                    obj.update(annotated_obj)
                    queried_objs += 1
                for key in ['is_food', 'is_drink', 'is_holdable', 'is_wearable', 'is_wieldable', 'is_surface', 'is_container']:
                    if key not in obj:
                        print(obj)
                assert obj.get()
        except:
            pass

    print(f"Events: {tot_events}\nObjs: {tot_objs}\nFound: {db_objs}\nQueried: {queried_objs}\nDone: {done_objs}")

    with open(EVENTS_OUTPUT_FILE, 'w+') as json_file:
        json.dump(events, json_file)

    print("Bye!")

