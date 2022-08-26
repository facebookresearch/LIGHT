from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
import pickle

db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)

DO_REVIEW = True

task_names = ["objects-interaction-task-allowlist-constraints-3"]

units = []
for t in task_names:
    new_units = mephisto_data_browser.get_units_for_task_name(t)
    units.extend(new_units)

accepted_units = [u for u in units if u.get_status() == "accepted"]
event_data = [mephisto_data_browser.get_data_from_unit(unit) for unit in accepted_units]

valid_start = int(len(event_data) * 0.8)

test_start = valid_start + int(len(event_data) * 0.1)

SPLITS = {}
cur_split = "train"
i = 0
for split, end in [("train", valid_start), ("valid", test_start), ("test", len(event_data))]:
    USE_EVENT_DATA = []
    while i < end:
        data = event_data[i]
        task_state = data['data']['outputs']['this_task_state']
        
        is_secondary_held = task_state['isSecondaryHeld']
        raw_action = task_state['rawAction']
        narration = task_state['interaction']
        object1 = task_state['object1']['name']
        object2 = task_state['object2']['name']
        non_actor_narration = task_state["broadcastMessage"].replace("villager", "ACTOR")
        # non_actor_narration = non_actor_narration.replace(object1, "OBJECT1")
        # non_actor_narration = non_actor_narration.replace(object2, "OBJECT2")
        # if "ACTOR" not in non_actor_narration:
        #     print(f"OH NO: {non_actor_narration}")
        #     print(task_state['interaction'])
        #     continue
        # if "OBJECT1" not in non_actor_narration:
        #     print(f"OH NO1: {non_actor_narration}")
        #     continue
        # if "OBJECT2" not in non_actor_narration:
        #     print(f"OH NO2: {non_actor_narration}")
        #     continue

        USE_EVENT_DATA.append(data)
        i += 1
    SPLITS[split] = USE_EVENT_DATA

# with open('/private/home/alexgurung/ParlAI/data/light_common_sense/use_events.pkl', 'wb') as f:
with open('/private/home/alexgurung/ParlAI/data/light_common_sense/gameplays/use_events.pkl', 'wb') as f:
    pickle.dump(SPLITS, f)

