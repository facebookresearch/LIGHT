"""
Validates if the given no-op-actions auto-grounding confirms
that the starting elements remain and in their same locations.
"""

import os
import json
import shutil
from .utils import lev_dist

from typing import Dict, Any, List, Optional

TARGET_FILE = os.path.join(os.path.dirname(__file__), "out_data", "no-op-actions.json")
BACKUP_FILE = TARGET_FILE + ".bak"


def main():
    if os.path.exists(BACKUP_FILE):
        print("Backup file still exists, perhaps something went wrong last run? Check and remove before continuing")
        return
    results = {}
    if os.path.exists(TARGET_FILE):
        shutil.copyfile(TARGET_FILE, BACKUP_FILE)
        with open(TARGET_FILE, 'r') as target_file:
            results = json.load(target_file)

    current_results_len = len(results)
    print("Existing narrations: ", current_results_len)
    current_results_len_json = len(json.dumps(results))

    failed_annotations = 0
    succeeded_annotations = 0
    total_annotations = 0
    for example in list(results.values()):
        try:
            if example['edit_data'] is not None:
                total_annotations += 1
                continue
            if example['object_attributes']['before'] is None:
                failed_annotations += 1
                continue
            lower_list = [l.lower() for l in example['objects_afterwards']]
            if len(lower_list) != 2:
                failed_annotations += 1
                continue
            if not (lev_dist(example['primary'].lower(), lower_list[0]) <= 3 or lower_list[0] in example['primary'].lower()):
                failed_annotations += 1
                continue
            if not (lev_dist(example['secondary'].lower(), lower_list[1]) <= 3 or lower_list[1] in example['secondary'].lower()):
                failed_annotations += 1
                continue
            locations_static = True
            for k, v in example['locations_afterwards'].items():
                if not v.startswith("original location of "):
                    locations_static = False
                    break
                target = v[len("original location of ")]
                if not (lev_dist(k, target) <= 3 or target in k):
                    locations_static = False
            if not locations_static:
                failed_annotations += 1
                continue
            example['edit_data'] = {
                "interactionValid": True,
                "usesExternalContext": True, # we only have one narration
                "updatedNarration": example['action_desc'],
                "primaryItem": example['primary'],
                "externalPerspective": example['external_perspective'],
                "remainingObjects": [example['primary'], example['secondary']],
                "finalDescriptions": {
                    example['primary']: example['primary_desc'],
                    example['secondary']: example['secondary_desc'],
                },
                'finalLocations': {
                    example['primary']: "original location of " + example['primary_desc'],
                    example['secondary']: "original location of " + example['secondary_desc'],
                },
                "beforeAttributes": {
                    example['primary']: {'EXTRAS': ""},
                    example['secondary']: {'EXTRAS': ""},
                },
                "afterAttributes": {
                    example['primary']: {'EXTRAS': ""},
                    example['secondary']: {'EXTRAS': ""},
                },
            }
            succeeded_annotations += 1
            total_annotations += 1
        except (AssertionError) as e:
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
