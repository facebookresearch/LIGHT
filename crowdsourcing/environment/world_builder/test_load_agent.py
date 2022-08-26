from common_sense_agent_utils import CommonSenseAgent
import json
from graph_converter_utils import add_object_to_graph, add_character_to_graph, get_room_content_from_json, replace_binarized_attributes_with_description, run_create_char, run_create_obj, modify_room_attrs

model_name = "bart_all_simple_Sun_Jan_23/c9d"

# force = False
force = True

with open(f"/checkpoint/alexgurung/light/common_sense/add_format/{model_name}/model.opt") as f:
    opt = json.load(f)

if "override" not in opt:
    opt['override'] = {}
opt['override']['skip_generation'] = False

agent = CommonSenseAgent(
    opt, model_name=model_name, force_add=force, verbose=False, count_errors=True
)

# graph = """Local Inn -=- IS_TYPE -=- ROOM
# Local Inn -=- HAS_DESCRIPTION -=- The local inn is an old renovated barn, and it shows."""

empty_graph = {'db_id': 18, 
                'base_id': 17, 'category': None, 
                'setting': 'Southernmost Tower Entryway', 
                'description': 'The rather drab tower was made of gray stones approximately all the same size. Artwork hung on the walls depicting battle scenes from long ago but even the color from these had faded with time. The cold, outside air seeped in through every small crack and crevice leaving a damp quality to the air. Sealed off rooms lined the perimeter and obviously had not been seen by human eyes for centuries.', 
                # 'background': 'This tower was the first built to accompany the castle and was majestic in its heyday. It stood four stories tall, gleaming white with parapets on the top. The Southernmost Tower served as the guest quarters for visitors to the castle and was talked about throughout the land. After the Heinous Wars the castle was left to rot when its inhabitants fled for their lives. The castle and its accompanying tower stand as a footnote in history now.', 
                'background': '', 
                'neighbors': None, 'possible_connections': {}, 'data_split': None, 'objects': [], 'characters': [], 'element_type': 'room'}


# Local Inn -=- HAS_BACKSTORY -=- The local inn is the favorite establishment of many a drunkard and off-duty soldier."""

# new_graph = agent.add_room_backstory(empty_graph)
# print(agent.parse_room_graph(new_graph))


incoming_graph_format = {
    "id":1,
    "name": "Starter World",
    "tags":[],
    "agents": [],
    "nodes": {},
    "objects": [],
    "rooms": []
}

example_world = {
    "id":1,
    "name": "Simple World",
    "tags":["#red", "#haunted", "#dry"],
    "agents": ["kitty_3_5", "orc_2_4"],
    "nodes": {
      "church_entryway_1_2": {
        "agent": False,
        "classes": ["room"],
        "contain_size": 100000,
        "contained_nodes": {
          "kitty_3_5": {
            "target_id": "kitty_3_5"
          },
          "muddy_area_6_7": {
            "target_id": "muddy area_6_7"
          },
          "scroll_9_1": {
            "target_id": "scroll_9_1"
          },
          "scroll_9_2": {
            "target_id": "scroll_9_2"
          },
          "scroll_9_3": {
            "target_id": "scroll_9_3"
          },
          "shovel_5_6": {
            "target_id": "shovel_5_6"
          }
        },
        "container_node": {
          "target_id": "VOID"
        },
        "db_id": None,
        "desc": "The church has marble floors and a huge frost window. There are benches made from wood and a big organ can be seen at the front stage. There is gold trim all around the church.",
        "extra_desc": "The church has marble floors and a huge frost window. There are benches made from wood and a big organ can be seen at the front stage. There is gold trim all around the church.",
        "name": "Church Entryway",
        "name_prefix": "the",
        "names": ["Church Entryway"],
        "neighbors": {
          "orc_cave_0_1": {
            "examine_desc": "You see a path!",
            "label": "path to the west",
            "locked_edge": None,
            "target_id": "orc cave_0_1"
          }
        },
        "node_id": "church entryway_1_2",
        "object": False,
        "room": True,
        "size": 1,
        "grid_location": [0, 0, 0],
        "surface_type": "in"
      },
      "kitty_3_5": {
        "agent": True,
        "aggression": 0,
        "pacifist": False,
        "char_type": "creature",
        "classes": ["agent"],
        "contain_size": 20,
        "contained_nodes": {},
        "container_node": {
          "target_id": "church entryway_1_2"
        },
        "damage": 1,
        "db_id": None,
        "defense": 0,
        "desc": "Black and white and cute all over.",
        "followed_by": {},
        "following": None,
        "food_energy": 1,
        "health": 5,
        "is_player": False,
        "name": "kitty",
        "name_prefix": "a",
        "names": ["kitty"],
        "tags": ["orc"],
        "node_id": "kitty_3_5",
        "object": False,
        "on_events": None,
        "persona": "I'm a cute kitty.",
        "room": False,
        "size": 20,
        "speed": 20
      },
      "muddy_area_6_7": {
        "agent": False,
        "classes": ["object"],
        "contain_size": 20,
        "contained_nodes": {},
        "container": True,
        "container_node": {
          "target_id": "church entryway_1_2"
        },
        "db_id": None,
        "dead": False,
        "desc": "A muddy area.",
        "drink": False,
        "equipped": None,
        "food": False,
        "food_energy": 0,
        "gettable": False,
        "locked_edge": None,
        "name": "muddy area",
        "name_prefix": "a",
        "names": ["muddy area"],
        "node_id": "muddy area_6_7",
        "object": True,
        "on_use": None,
        "room": False,
        "size": 1,
        "stats": {
          "damage": 0,
          "defense": 0
        },
        "surface_type": "in",
        "value": 1,
        "wearable": False,
        "wieldable": False
      },
      "orc_cave_0_1": {
        "agent": False,
        "classes": ["room"],
        "contain_size": 100000,
        "contained_nodes": {
          "orc_2_4": {
            "target_id": "orc_2_4"
          }
        },
        "container_node": {
          "target_id": "VOID"
        },
        "db_id": None,
        "desc": "It is a dark cave that is cold and damp inside. The floor is rocks covered in bat poop. It is damp from the ceiling dripping of water. The cave just goes on what seems to be endlessly into the dark abyss. The only light you can see is from the distance entrance of the cave.",
        "extra_desc": "It is a dark cave that is cold and damp inside. The floor is rocks covered in bat poop. It is damp from the ceiling dripping of water. The cave just goes on what seems to be endlessly into the dark abyss. The only light you can see is from the distance entrance of the cave.",
        "name": "Orc cave",
        "name_prefix": "the",
        "names": ["Orc cave"],
        "neighbors": {
          "church_entryway_1_2": {
            "examine_desc": "You see a path!",
            "label": "path to the east",
            "locked_edge": None,
            "target_id": "church entryway_1_2"
          }
        },
        "node_id": "orc cave_0_1",
        "object": False,
        "room": True,
        "size": 1,
        "grid_location": [1, 0, 0],
        "surface_type": "in"
      },
      "orc_2_4": {
        "agent": True,
        "usually_npc": True,
        "aggression": 0,
        "char_type": "creature",
        "classes": ["agent"],
        "contain_size": 20,
        "contained_nodes": {
          "priceless_piece_of_art_4_3": {
            "target_id": "priceless piece of art_4_3"
          }
        },
        "container_node": {
          "target_id": "orc cave_0_1"
        },
        "damage": 1,
        "db_id": None,
        "defense": 0,
        "desc": "You really don't have a good reason to be examining this orc closer.",
        "followed_by": {},
        "following": None,
        "food_energy": 1,
        "health": 10,
        "is_player": False,
        "name": "orc",
        "name_prefix": "an",
        "names": ["orc"],
        "node_id": "orc_2_4",
        "object": False,
        "tags": ["orc"],
        "attack_tagged_agents": ["!orc"],
        "dont_accept_gifts": False,
        "on_events": [
          [
            ["SayEvent", "lotr"],
            ["SayEvent", "One does not simply mention lotr!"]
          ],
          [
            ["SayEvent", "art"],
            [
              "SayEvent",
              "I might give you this piece of art if you give me something shiny for it."
            ]
          ],
          [
            ["SayEvent", "smile at me"],
            ["EmoteEvent", "smile"]
          ],
          [
            ["GiveObjectEvent", "ring"],
            ["GiveObjectEvent", "art", "other_agent"]
          ]
        ],
        "persona": "I am a orc that was born in a cave. I eat corn the most. I have many friends.",
        "room": False,
        "size": 20,
        "speed": 20
      },
      "priceless_piece_of_art_4_3": {
        "agent": False,
        "classes": ["object"],
        "contain_size": 0,
        "contained_nodes": {},
        "container": False,
        "container_node": {
          "target_id": "orc_2_4"
        },
        "db_id": None,
        "dead": False,
        "desc": "A work of art that is has more than monetary value. Mostly owned by kings and wealthy collectors",
        "drink": False,
        "equipped": None,
        "food": False,
        "food_energy": 0,
        "gettable": True,
        "locked_edge": None,
        "name": "priceless piece of art",
        "name_prefix": "a",
        "names": ["priceless piece of art"],
        "node_id": "priceless piece of art_4_3",
        "object": True,
        "on_use": None,
        "room": False,
        "size": 1,
        "stats": {
          "damage": 0,
          "defense": 0
        },
        "surface_type": "on",
        "value": 10,
        "wearable": False,
        "wieldable": True
      },
      "shovel_5_6": {
        "agent": False,
        "classes": ["object"],
        "contain_size": 0,
        "contained_nodes": {},
        "container": False,
        "container_node": {
          "target_id": "church entryway_1_2"
        },
        "db_id": None,
        "dead": False,
        "desc": "A shovel",
        "drink": False,
        "equipped": None,
        "food": False,
        "food_energy": 0,
        "gettable": True,
        "locked_edge": None,
        "name": "shovel",
        "name_prefix": "a",
        "names": ["shovel"],
        "node_id": "shovel_5_6",
        "object": True,
        "on_use": [
            {
            "remaining_uses": 1,
            "events": [
              {
                "type": "create_entity",
                "params": {
                  "type": "in_used_target_item",
                  "object": {
                    "name_prefix": "an",
                    "is_wearable": True,
                    "name": "emerald ring",
                    "desc": "A beautiful and mysterious ring.. could it have magical powers?"
                  }
                }
              },
              {
                "type": "broadcast_message",
                "params": {
                  "self_view": "You dig into the sodden mud, and spy something glistening within!"
                }
              }
            ],
            "constraints": [
              {
                "type": "is_holding",
                "params": {
                  "complement": "used_item"
                }
              },
              {
                "type": "used_with_item_name",
                "params": {
                  "item": "muddy area"
                }
              }
            ]
          }
        ],
        "room": False,
        "size": 1,
        "stats": {
          "damage": 1,
          "defense": 0
        },
        "surface_type": "on",
        "value": 1,
        "wearable": False,
        "wieldable": True
      },
      "scroll_9_1": {
        "agent": False,
        "desc": "An old scroll with words you decipher to be\": \"facere mortem\". Could this be magic?",
        "name": "mortem scroll",
        "drink": False,
        "equipped": None,
        "food": True,
        "food_energy": 2,
        "name_prefix": "a",
        "value": 10,
        "node_id": "scroll_9_1",
        "container_node": {
            "target_id": "church entryway_1_2"
        },
        "contained_nodes": {},
      "object": True,
        "on_use": [
          {
            "events": [
              {
                "type": "broadcast_message",
                "params": {
                  "self_view": "You say the words aloud, and runes on the scroll glow with gold.",
                  "self_as_target_view": "You are struck with searing pain!",
                  "self_not_target_view": "{recipient_text} is struck with searing pain!",
                  "room_view": "{actor_text} says the words of a scroll aloud, and it glows with gold. {recipient_text} is struck with searing pain!"
                }
              },
              {
                "type": "modify_attribute",
                "params": {
                  "type": "in_used_target_item",
                  "key": "health",
                  "value": "-20"
                }
              }
            ],
            "constraints": [
              {
                "type": "is_holding",
                "params": {
                  "complement": "used_item"
                }
              },
              {
                "type": "used_with_agent"
              }
            ]
          }
        ]
      },
      "scroll_9_2": {
        "agent": False,
        "classes": ["object"],
        "desc": "An old scroll with words you decipher to be: \"creo magnitudo\". Could this be magic?",
        "name": "magnitudo scroll",
        "name_prefix": "a",
        "node_id": "scroll_9_2",
        "container_node": { "target_id": "church entryway_1_2" },
        "contained_nodes": {},
        "object": True,
        "on_use": [
          {
            "events": [
              {
                "type": "broadcast_message",
                "params": {
                  "self_view": "You say the words aloud, and runes on the scroll glow with gold.",
                  "self_as_target_view": "Suddenly you feel a voluminous about you and you feel ... LARGER! You are  growing!",
                  "self_not_target_view": "{recipient_text} appears to be growing larger!!!",
                  "room_view": "{actor_text} says the words of a scroll aloud, and it glows with gold. {recipient_text} seems to glow for a second.. and appears to be getting larger!"
                }
              },
              {
                "type": "modify_attribute",
                "params": {
                  "type": "in_used_target_item",
                  "key": "size",
                  "value": "+2"
                }
              }
            ],
            "constraints": [
              {
                "type": "is_holding",
                "params": {
                  "complement": "used_item"
                }
              },
              {
                "type": "used_with_agent"
              }
            ]
          }
        ]
      },
      "scroll_9_3": {
        "agent": False,
        "classes": ["object"],
        "desc": "An old scroll with words you decipher to be: \"creo dexteritate\". Could this be magic?",
        "name": "dexteritate scroll",
        "name_prefix": "a",
        "node_id": "scroll_9_3",
        "container_node": { "target_id": "church entryway_1_2" },
        "contained_nodes": {},
        "object": True,
        "on_use": [
          {
            "events": [
              {
                "type": "broadcast_message",
                "params": {
                  "self_view": "You say the words aloud, and runes on the scroll glow with gold.",
                  "self_as_target_view": "Suddenly you feel a lightness upon you and you feel more fleet of foot. Your dexterity has increased!",
                  "self_not_target_view": "{recipient_text} feels a lightness upon them and they feel more fleet of foot. Their dexterity has increased!",
                  "room_view": "{actor_text} says the words of a scroll aloud, and it glows with gold. {recipient_text} seems to glow for a second."
                }
              },
              {
                "type": "modify_attribute",
                "params": {
                  "type": "in_used_target_item",
                  "key": "dexterity",
                  "value": "+2"
                }
              }
            ],
            "constraints": [
              {
                "type": "is_holding",
                "params": {
                  "complement": "used_item"
                }
              },
              {
                "type": "used_with_agent"
              }
            ]
          }
        ]
      }
    },
    "objects": [
      "muddy area_6_7",
      "priceless piece of art_4_3",
      "shovel_5_6",
      "scroll_9_1",
      "scroll_9_2",
      "scroll_9_3"
    ],
    "rooms": ["church entryway_1_2", "orc cave_0_1"]
}

print(example_world.keys())

for k in example_world.keys():
    print(f"{k}\t{type(example_world[k])}")

# print(example_world['rooms'])
# for r in example_world['rooms']
# print(example_world['nodes'].keys())

example_world['rooms'] = [r.replace(" ", "_") for r in example_world['rooms']]
example_world['objects'] = [r.replace(" ", "_") for r in example_world['objects']]
# example_world['nodes'] = [r.replace(" ", "_") for r in example_world['objects']]
example_world['agents'] = [r.replace(" ", "_") for r in example_world['agents']]
# print(example_world['nodes'])
for n, node in example_world['nodes'].items():
    print(n, node['contained_nodes'])


cur_room = example_world['rooms'][0]
# cur_room = example_world['rooms'][1]

example_world['rooms'] = [cur_room]


print(f"SHOULD HAVE THESE OBJECTS")
objs = [o.replace(" ", "_") for o in example_world['objects']]
for o in objs:
    node = example_world['nodes'][o]
    parent = node['container_node']['target_id'].replace(" ", "_")
    if parent == cur_room:
        print(node['name'])
        node['container_node']

print(f"SHOULD HAVE THESE CHARACTERS")
chars = [c.replace(" ", "_") for c in example_world['agents']]
for c in chars:
    node = example_world['nodes'][c]
    parent = node['container_node']['target_id'].replace(" ", "_")
    if parent == cur_room:
        print(node['name'])

print("-"*40)

graph = get_room_content_from_json(example_world)
print(graph.keys())
print(graph['setting'])
print('*'*30)
# print(example_)
########################
# Backstory
########################
graph = agent.add_room_backstory(graph)
example_world = modify_room_attrs(example_world, cur_room, "extra_desc", graph["background"])
########################
# Description
########################
graph = agent.add_room_description(graph)
example_world = modify_room_attrs(example_world, cur_room, "desc", graph["description"])

########################
# Add Object
########################
graph, obj_name_diff = run_create_obj(graph, agent, count=3)
new_objects = [o for o in graph['objects'] if o['name'] in obj_name_diff]
print(f"all objects: {[o['name'] for o in graph['objects']]}")
print(f"new objects: {[o['name'] for o in new_objects]}")
for o in new_objects:
  example_world = add_object_to_graph(example_world, cur_room, o)

########################
# Add Character
########################
print(f"all chars: {[o['name'] for o in graph['characters']]}")
graph, char_name_diff = run_create_char(graph, agent, count=3)
new_chars = [c for c in graph['characters'] if c['name'] in char_name_diff]
print(f"all chars: {[o['name'] for o in graph['characters']]}")
print(f"new chars: {[o['name'] for o in new_chars]}")
for c in new_chars:
  example_world = add_character_to_graph(example_world, cur_room, c)

########################
# Add Character Secondary Objects
########################
for c in new_chars:
  og_secondary_objects = example_world['nodes']
  graph = agent.add_character_carrying(
      graph, c['name'], count=3
  )
  graph = agent.add_character_wearing(
      graph, c['name'], count=3
  )
  graph = agent.add_character_wielding(
      graph, c['name'], count=3
  )


for c in graph['characters']:
  print(c)

print("~~~~~")
for c in graph['objects']:
  print(c)

print("-"*100)

print(replace_binarized_attributes_with_description(agent.parse_room_graph(graph)))

print("-"*100)
def get_nice_parts_of_node(node):
  good_attrs = set(["name", "persona", "desc", "contained_nodes"])
  return {k:v for k, v in node.items() if k in good_attrs}

def get_nice_name(name):
  return name.replace(" ", "_")

sub_nodes = {n:get_nice_parts_of_node(node) 
              for n, node in example_world['nodes'].items() 
              if n == cur_room or get_nice_name(node['container_node']['target_id']) == get_nice_name(cur_room)}
print(sub_nodes)