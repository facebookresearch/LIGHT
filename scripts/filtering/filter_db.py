import os
import pickle

from light.data_model.light_database import LIGHTDatabase, DB_STATUS_REJECTED

# db_path = '/Users/jju/ParlAI/data/LIGHT/environment/db/database3.db'
# db_path = '/Users/jju/Desktop/ParlAI/data/LIGHT/environment/db/database3.db'
db_path = "/Users/jju/tmp_packages/tmp_packages/light_package/database.db"

rejected_count = 0
rejected_rooms = 0
kept_rooms = 0

BAD_WORDS = ["sex", "wench", "torture"]

with LIGHTDatabase(db_path) as db:
    rooms = db.get_room()
    for room in rooms:
        status = db.get_id(room["id"])
        if status[0]["status"] == DB_STATUS_REJECTED:
            rejected_rooms += 1
            contents = db.get_node_content(parent_id=room["id"])
            for c in contents:
                db.update_status(c["child_id"], DB_STATUS_REJECTED)
        else:
            kept_rooms += 1
            # db.update_status()
    all_items = db.get_id(expand=True)
    for item in all_items:
        dict_item = dict(item)
        for key, value in dict_item.items():
            if isinstance(value, str):
                for word in BAD_WORDS:
                    if word in value.lower():
                        db.update_status(dict_item["id"], DB_STATUS_REJECTED)

print(rejected_count, rejected_rooms, kept_rooms)
# print(status[0]['status'], DB_STATUS_REJECTED)
# contents = db.get_node_content(parent_id=rooms[0]['id'])
# print(contents)

# print([c['id'] for c in contents])
# print([c['child_id'] for c in contents])
# print([dict(db.get_id(c['child_id'], expand=True)[0]) for c in contents][:3])
