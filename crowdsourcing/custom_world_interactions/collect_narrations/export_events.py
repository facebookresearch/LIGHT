import json
import os
import random
from .utils import lev_dist
from collections import defaultdict

from typing import Dict, Any, List, Tuple, TypedDict, Optional

TARGET_FILE = os.path.join(os.path.dirname(__file__), "out_data", "results.json")

EVENTS_OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "out_data", "events.json")

"""
Takes the crowdsourced results.json file and outputs an events 
file (for the main database use and import) and a commonsense 
file (for use for the commonsense project)
"""

class AttributeData(TypedDict):
    before: Dict[str, Dict[str, str]] # Map from object name to attribute => reason map
    after: Dict[str, Dict[str, str]]

class EditData(TypedDict):
    interactionValid: bool # Whether the interaction is seen as valid
    usesExternalContext: bool # If the interaction's original description relies on external context
    updatedNarration: str # Alternate description of the interaction
    primaryItem: str # one of obj1 name, obj2 name, either, both
    externalPerspective: str # Corrected external description for the interaction
    remainingObjects: List[str] # Corrected list of remaining objects
    finalDescriptions: Dict[str, str] # Corrected final descriptions for objects
    finalLocations: Dict[str, str] # Corrected final locations of objects
    beforeAttributes: Dict[str, Dict[str, str]] # Dict of objects to attribute => reason links
    afterAttributes: Dict[str, Dict[str, str]] # Dict of objects to attribute => reason links

class Result(TypedDict):
    id: str # id into result map
    primary: str # Name of obj 1
    primary_desc: str # description of obj 1
    secondary: str # name of obj 2
    secondary_desc: str # description of obj 2
    raw_action: str # action text replacing use X with Y
    action_desc: str # First person description for the action
    review_status: Any # unused for the most part
    external_perspective: str # Extternal view for this action
    objects_afterwards: List[str] # list of remaining object names
    descriptions_afterwards: Dict[str, str] # GENERATED Map from object name to description after event
    locations_afterwards: Dict[str, str] # GENERATED Map from object name to location after event
    objects_afterwards: AttributeData # GENERATED Map from object name + before/after to attribute and reason
    edit_data: EditData # Human (usually) provided edit-data

class Obj(TypedDict):
    name: str # Name of the object
    desc: str # text description for the object
    change: str # one of "ADDED", "REMOVED", "RETAINED"

class Attribute(TypedDict):
    name: str # Name of the attribute
    removed: bool # If this attribute is removed

class Event(TypedDict):
    obj1: Obj
    obj2: Obj
    raw_action: str # freeform text trigger
    primary_type: str # obj1, obj2, both, either
    action_desc: str # first person description for action
    action_desc_alternate: Optional[str] # string for an alternate action description
    action_desc_external: str # external description template for action
    objects_afterwards: List[Obj] # remaining objects
    final_locations: Dict[str, Tuple[str, str]] # Locations for all the remaining objects
    before_attributes: Dict[str, List[Attribute]] # object names to attribute lists (constraints)
    after_attributes: Dict[str, List[Attribute]] # object names to attribute lists (effects)


def result_to_event(result: Result) -> Event:
    """Given a crowdsourced result, convert it to a directly usable event format"""
    # Determine which object is primary and secondary in the event
   result['primary'] = result['primary'].strip()
   result['secondary'] = result['secondary'].strip()
   event_type_map = {
        result['primary']: 'obj1',
        result['secondary']: 'obj2',
        'both': 'both',
        'either': 'either',
    }

    # Extract the main description and alternate description.
    if result['edit_data']['usesExternalContext']:
        action_desc = result['edit_data']['updatedNarration'].strip()
        action_desc_alternate = None
    else: 
        action_desc = result['action_desc'].strip()
        action_desc_alternate = result['edit_data']['updatedNarration'].strip()

    # Extract the final object list
    orig_names = [result['primary'], result['secondary']]
    final_names = [n.lower() if n.lower() in orig_names else n for n in result['edit_data']['remainingObjects']]
    for n in list(result['edit_data']['finalDescriptions'].keys()):
        result['edit_data']['finalDescriptions'][n.lower()] = result['edit_data']['finalDescriptions'][n]
    final_objs = [
        {
            "name": name.strip(),
            "desc": result['edit_data']['finalDescriptions'][name.strip().lower()],
            "change": "RETAINED" if name in orig_names else "ADDED",
        } for name in final_names
    ]

    # figure out which before attributes are required, and which ones are altered
    before_atts = {}
    for obj_name, att_dict in result['edit_data']['beforeAttributes'].items():
        extras = att_dict['EXTRAS']
        del att_dict['EXTRAS']
        retained_attrs = []
        for k, v in att_dict.items():
            if 'not required' in v.lower():
                continue
            if k.strip() == '':
                continue
            retained_attrs.append({
                "name": k, "removed": "REMOVED" in v
            })
        extras_list = extras.split(',')
        for extra in extras_list:
            extra = extra.strip()
            if len(extra.split(' ')) > 5:
                continue # this is an explanation, not an extra
            if len(extra) == 0:
                continue
            removed = False
            if 'REMOVED' in extra:
                extra = extra.split('REMOVED')[0].strip()
                removed = True
            retained_attrs.append({'name': extra, 'removed': removed})
        before_atts[obj_name] = retained_attrs

    # Figure out which attributes are added afterwards
    after_attrs = {}
    for obj_name, att_dict in result['edit_data']['afterAttributes'].items():
        extras = att_dict['EXTRAS']
        del att_dict['EXTRAS']
        retained_attrs = []
        for k, v in att_dict.items():
            if 'not required' in v.lower():
                continue
            if k.strip() == '':
                continue
            retained_attrs.append({
                "name": k, "removed": False
            })
        extras_list = extras.split(',')
        for extra in extras_list:
            extra = extra.strip()
            if extra == '':
                continue
            if len(extra.split(' ')) > 5:
                continue # this is an explanation, not an extra
            retained_attrs.append({'name': extra, 'removed': False})
        after_attrs[obj_name] = retained_attrs

    # Convert the locations to standard format
    def extract_tag_for_location(location: str) -> Tuple[str, str]:
        location = location.lower()
        if 'original location of ' in location:
            target = location.split('original location of ')[-1]
            for idx, n in enumerate(orig_names):
                if target in n.lower():
                    return ('at', orig_names[idx])
            for idx, n in enumerate(orig_names):
                if n.lower().strip('s') in target:
                    return ('at', orig_names[idx])
            for idx, n in enumerate(orig_names):
                if lev_dist(n.lower(), target) <= max(len(n) / 2, len(target) / 2):
                    return ('at', orig_names[idx])
            for item_name, val in result['edit_data']['finalDescriptions'].items():
                # IDK but one worker seemed to be putting in descriptions here...
                if val.lower() == target:
                    return ('at', item_name)
            for item_name, val in [(result['primary'], result['primary_desc']), (result['secondary'], result['secondary_desc'])]:
                # IDK but one worker seemed to be putting in descriptions here...
                if val.lower() == target:
                    return ('at', item_name)
            raise Exception(f"Could not find {target} in {orig_names}")
        elif location.startswith('inside '):
            target = location[len('inside '):]
            loc_type = 'in'
        elif location.startswith('in '):
            target = location[len('in '):]
            loc_type = 'in'
        elif location.startswith('on '):
            target = location[len('on '):]
            loc_type = 'on'
        elif ' into ' in location:
            target = location.split(' into ')[-1]
            loc_type = 'in'
        elif ' around ' in location:
            target = location.split(' around ')[-1]
            loc_type = 'on'
        elif location.startswith('held by ') or lev_dist(location, "held by actor") < 4:
            return ('held', 'actor')
        elif location.startswith('worn by ') or lev_dist(location, "worn by actor") < 4:
            return ('worn', 'actor')
        elif location.startswith('wielded by ') or lev_dist(location, "wielded by actor") < 4:
            return ('wielded', 'actor')
        else:
            if 'room' in location:
                return ('in', 'room')
            for item_name in orig_names + final_names:
                # try any matching, really
                if item_name in location:
                    if ' in ' in location:
                        return ('in', item_name)
                    elif ' on ' in location:
                        return ('on', item_name)
                    return ('at', item_name)
            raise Exception(f"Format of {location} does not match expected")
        target = target.strip("the ")
        if target in ['room', 'ro0m', 'ground', 'floor']:
            return ('in', 'room')
        if 'room' in target:
            return ('in', 'room')
        if target in ['actor']:
            return ('held', 'actor')
        for idx, n in enumerate(final_names):
            if target in n.lower():
                return (loc_type, final_names[idx])
        for idx, n in enumerate(final_names):
            if n.lower().strip('s') in target:
                return (loc_type, final_names[idx])
        for idx, n in enumerate(final_names):
            if lev_dist(n.lower(), target) <= max(len(n) / 2, len(target) / 2):
                return (loc_type, final_names[idx])
        for item_name, val in result['edit_data']['finalDescriptions'].items():
            # IDK but one worker seemed to be putting in descriptions here...
            if val.lower() == target:
                return (loc_type, item_name)
        for item_name, val in [(result['primary'], result['primary_desc']), (result['secondary'], result['secondary_desc'])]:
            # IDK but one worker seemed to be putting in descriptions here...
            if val.lower() == target:
                return (loc_type, item_name)
        raise Exception(f"Could not find {target} in {final_names}")

    lower_final_names = [n.lower() for n in final_names]
    for obj_name, loc in result['edit_data']['finalLocations'].items():
        if loc == "original location":
            result['edit_data']['finalLocations'][obj_name] = f"original location of {obj_name}"

    locations = {
        obj_name: extract_tag_for_location(loc) 
        for obj_name, loc in result['edit_data']['finalLocations'].items()
        if obj_name.lower() in lower_final_names
    }

    for obj_name in final_names:
        assert obj_name in locations or obj_name.lower() in locations, f"{obj_name} not in {locations}"

    # Other cleanup
    if 'primaryItem' not in result['edit_data']:
        result['edit_data']['primaryItem'] = result['primary']

    # Produce final event
    event = {
        "obj1": {
            "name": result['primary'].strip(),
            "desc": result['primary_desc'].strip(),
            "change": "RETAINED" if result['primary'] in final_names else "REMOVED",
        },
        "obj2": {
            "name": result['secondary'].strip(),
            "desc": result['secondary_desc'].strip(),
            "change": "RETAINED" if result['secondary'] in final_names else "REMOVED",
        },
        "primary_type": event_type_map[result['edit_data']['primaryItem']],
        "raw_action": result['raw_action'].strip(),
        "action_desc": action_desc,
        "action_desc_alternate": action_desc_alternate,
        "action_desc_external": result['edit_data']['externalPerspective'].strip(),
        "objects_afterwards": final_objs,
        "final_locations": locations,
        "before_attributes": before_atts,
        "after_attributes": after_attrs,
    }
    return event


def segment_events(events: List[Event]) -> Dict[str, List[Event]]:
    """Split a group of events into train/test/valid/unseen"""
    TEST_COUNT = 500
    VALID_COUNT = 500
    UNSEEN_TARGET = 500

    events_by_obj = defaultdict(list)
    for event in events:
        events_by_obj[event['obj1']['name'].lower()].append(event)
        events_by_obj[event['obj2']['name'].lower()].append(event)
    
    sorted_events_by_obj = [(obj, len(v)) for obj, v in events_by_obj.items()]
    sorted_events_by_obj.sort(key=lambda x: x[1], reverse=True)
    unseen_count = 0
    unseen_objs = []
    for obj, count in sorted_events_by_obj:
        if count > UNSEEN_TARGET / 10:
            continue # We want some diversity in these unseens
        unseen_objs.append(obj.lower())
        unseen_count += count
        if unseen_count >= UNSEEN_TARGET:
            break # We're done!
    assert unseen_count >= UNSEEN_TARGET

    unseen_set = []
    for obj_name in unseen_objs:
        unseen_set += events_by_obj[obj_name.lower()]
    
    seen_set = []
    for event in events:
        if event['obj1']['name'].lower() in unseen_objs:
            continue
        if event['obj2']['name'].lower() in unseen_objs:
            continue
        seen_set.append(event)
    
    random.shuffle(seen_set)
    return {
        'unseen': unseen_set,
        'valid': seen_set[:VALID_COUNT],
        'test': seen_set[VALID_COUNT:VALID_COUNT+TEST_COUNT],
        'train': seen_set[VALID_COUNT+TEST_COUNT:],
    }


def main():
    with open(TARGET_FILE) as target_file:
        results = json.load(target_file)
    
    events = []
    error_count = 0
    for result in results.values():
        if result['edit_data'] is None:
            continue
        if result['edit_data']['interactionValid'] is False:
            continue
        try:
            events.append(result_to_event(result))
        except Exception as e:
            if error_count < 100:
                import traceback
                traceback.print_exc()
            error_count += 1
            continue
    print(f"{len(events)} Results successfully converted to events")
    print(f"{error_count} Errors occurred")

    events_split = segment_events(events)
    with open(EVENTS_OUTPUT_FILE, "w+") as output_file:
        json.dump(events_split, output_file)


if __name__ == '__main__':
    main()
