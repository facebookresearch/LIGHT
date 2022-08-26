from light.data_model.light_database import LIGHTDatabase

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.metrics.pairwise import linear_kernel

from build_room_data import ROOM_ID_TO_ITEMS

import numpy as np

LIGHT_DB_PATH = "~/ParlAI/data/light/environment/db/d3/database3.db"
db = LIGHTDatabase(LIGHT_DB_PATH)

with db as ldb:
    all_objects = [dict(obj) for obj in ldb.get_object()]

print(f"len(all_objects): {len(all_objects)}")

with db as ldb:
    all_chars = [dict(obj) for obj in ldb.get_character()]

with db as ldb:
    all_rooms = [dict(obj) for obj in ldb.get_room()]

################################################################################################
#
# Room Vectorization Test
#
################################################################################################
print("#"*100)
print("#", "ROOM VECTORIZATION TEST")
print("#"*100)

room_vectorizer = TfidfVectorizer(stop_words="english")

room_texts = [room["name"] + "\n" + room['description'] for room in all_rooms]

room_vectors = room_vectorizer.fit_transform(room_texts)

test_room = {'name': "Castle", "desc": "A big castle."}
# test_room = {'name': "A big field", "desc": "A really ugly field."}

# test_new_room = "Field" + "\n" + "A field. clumped with plants and insects, and a pile of wheat."
# test_new_room = "The empire state building" + "\n" + "An iconic building, inside are some chairs."
test_room_text = test_room['name'] + '\n' + test_room['desc']

room_vec = room_vectorizer.transform([test_room_text])

cosine_similarities = linear_kernel(room_vec, room_vectors).flatten()

max_index = np.argmax(cosine_similarities)

inds = np.argpartition(cosine_similarities, -5)[-5:]
print(f"max inds: {inds}: {[cosine_similarities[i] for i in inds]}")

print(f"max index: {max_index}, value of {cosine_similarities[max_index]}")
print(f"Found Room:")

print(room_texts[max_index])
new_room = all_rooms[max_index]
print(new_room)
items = ROOM_ID_TO_ITEMS[new_room['id']]
for o in items['objects']:
    print(o['name'])
print("-"*100)
for c in items['characters']:
    print(c['name'])

################################################################################################
#
# OBJECT Vectorization Test
#
################################################################################################
print("#"*100)
print("#", "OBJECT VECTORIZATION TEST")
print("#"*100)

obj_vectorizer = TfidfVectorizer(stop_words="english")

obj_texts = [obj["name"] + "\n" + obj['physical_description'] for obj in all_objects]

obj_vectors = obj_vectorizer.fit_transform(obj_texts)

# test_obj = {'name': "Chair", "desc": "A weak chair, it might collapse"}
test_obj = {'name': "Chair", "desc": "A sturdy chair, it's for kings'"}

# test_new_room = "Field" + "\n" + "A field. clumped with plants and insects, and a pile of wheat."
# test_new_room = "The empire state building" + "\n" + "An iconic building, inside are some chairs."
test_obj_text = test_obj['name'] + '\n' + test_obj['desc']

obj_vec = obj_vectorizer.transform([test_obj_text])

cosine_similarities = linear_kernel(obj_vec, obj_vectors).flatten()

max_index = np.argmax(cosine_similarities)

inds = np.argpartition(cosine_similarities, -5)[-5:]
print(f"max inds: {inds}: {[cosine_similarities[i] for i in inds]}")

print(f"max index: {max_index}, value of {cosine_similarities[max_index]}")
print(f"Found obj:")

print(obj_texts[max_index])

################################################################################################
#
# OBJECT Vectorization Test
#
################################################################################################
print("#"*100)
print("#", "CHARACTER VECTORIZATION TEST")
print("#"*100)

char_vectorizer = TfidfVectorizer(stop_words="english")

char_texts = [char["name"] + "\n" + char['physical_description'] + "\n" + char["persona"] for char in all_chars]

char_vectors = char_vectorizer.fit_transform(char_texts)

# test_char = {'name': "Chair", "desc": "A weak chair, it might collapse"}
test_char = {'name': "rat", "physical_description": "A small rat, weak from starvation.", "persona": "A proud rat down on his luck."}

# test_new_room = "Field" + "\n" + "A field. clumped with plants and insects, and a pile of wheat."
# test_new_room = "The empire state building" + "\n" + "An iconic building, inside are some chairs."
test_char_text = test_char['name'] + '\n' + test_char['physical_description'] + "\n" + test_char["persona"]

char_vec = char_vectorizer.transform([test_char_text])

cosine_similarities = linear_kernel(char_vec, char_vectors).flatten()

max_index = np.argmax(cosine_similarities)

inds = np.argpartition(cosine_similarities, -5)[-5:]
print(f"max inds: {inds}: {[cosine_similarities[i] for i in inds]}")

print(f"max index: {max_index}, value of {cosine_similarities[max_index]}")
print(f"Found char:")

print(char_texts[max_index])

