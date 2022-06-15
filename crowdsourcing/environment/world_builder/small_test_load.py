from common_sense_agent_utils import CommonSenseAgent
import json
from graph_converter_utils import add_object_to_graph, add_character_to_graph, get_room_content_from_json, replace_binarized_attributes_with_description, run_create_char, run_create_obj, modify_room_attrs

model_name = "bart_all_simple_Sun_Jan_23/c9d"

force = False
# force = True

with open(f"/checkpoint/alexgurung/light/common_sense/add_format/{model_name}/model.opt") as f:
    opt = json.load(f)

if "override" not in opt:
    opt['override'] = {}
opt['override']['skip_generation'] = False

world_builder_agent = CommonSenseAgent(
    opt, model_name=model_name, force_add=force, verbose=False, count_errors=True
)
# args = {'target_room': 'Dungeon_1', 'room_graph': {'nodes': {'Dungeon_1': {'agent': False, 'brightness': None, 'classes': ['room'], 'contain_size': 0, 'contained_nodes': {'prisoner_1': {'target_id': 'prisoner_1'}, 'key_1': {'target_id': 'key_1'}}, 'db_id': None, 'is_indoors': None, 'desc': '', 'extra_desc': '', 'name': 'Dungeon', 'name_prefix': '', 'names': [], 'neighbors': [], 'node_id': 'Dungeon_1', 'object': False, 'room': True, 'size': 1, 'grid_location': [1, 0, 0], 'surface_type': '', 'temperature': None}, 'prisoner_1': {'agent': True, 'aggression': 0, 'attack_taggedAgents': [], 'blocked_by': {}, 'blocking': None, 'char_type': 'person', 'classes': ['agent'], 'contain_size': 0, 'contained_nodes': {}, 'container_node': {'target_id': 'Dungeon_1'}, 'damage': 1, 'db_id': None, 'dead': False, 'defense': 0, 'desc': '', 'dexterity': 0, 'dont_accept_gifts': False, 'followed_by': {}, 'follow': None, 'food_energy': 1, 'health': 2, 'is_player': False, 'max_distance_from_start_location': 1000000, 'max_wearable_items': 3, 'max_wieldable_items': 1, 'mission': '', 'movement_energy_cost': 0, 'name': 'prisoner', 'name_prefix': '', 'names': ['prisoner'], 'node_id': 'prisoner_1', 'num_wearable_items': 0, 'num_wieldable_items': 0, 'object': False, 'on_events': [], 'pacifist': False, 'persona': '', 'quests': [], 'size': 20, 'speed': 5, 'strength': 0, 'tags': [], 'usually_npc': False}, 'key_1': {'agent': False, 'classes': ['object'], 'contain_size': 0, 'contained_nodes': {}, 'container': False, 'container_node': {'target_id': 'Dungeon_1'}, 'db_id': None, 'dead': False, 'desc': '', 'drink': False, 'equipped': None, 'food': False, 'food_energy': 0, 'gettable': True, 'locked_edge': None, 'name': 'key', 'name_prefix': '', 'names': ['key'], 'node_id': 'key_1', 'object': True, 'on_use': None, 'room': False, 'size': 1, 'stats': {'damage': 0, 'defense': 0}, 'surface_type': 'on', 'value': 1, 'wearable': False, 'wieldable': False}}, 'agents': ['prisoner_1'], 'objects': ['key_1'], 'rooms': ['Dungeon_1']}}
args = {'target_room': 'Dungeon_1', 'room_graph': {'nodes': {'Dungeon_1': {'agent': False, 'brightness': None, 'classes': ['room'], 'contain_size': 0, 'contained_nodes': {}, 'db_id': None, 'is_indoors': None, 'desc': '', 'extra_desc': '', 'name': 'Dungeon', 'name_prefix': '', 'names': [], 'neighbors': [], 'node_id': 'Dungeon_1', 'object': False, 'room': True, 'size': 1, 'grid_location': [1, 0, 0], 'surface_type': '', 'temperature': None}, 'prisoner_1': {'agent': True, 'aggression': 0, 'attack_taggedAgents': [], 'blocked_by': {}, 'blocking': None, 'char_type': 'person', 'classes': ['agent'], 'contain_size': 0, 'contained_nodes': {}, 'container_node': {'target_id': 'Dungeon_1'}, 'damage': 1, 'db_id': None, 'dead': False, 'defense': 0, 'desc': '', 'dexterity': 0, 'dont_accept_gifts': False, 'followed_by': {}, 'follow': None, 'food_energy': 1, 'health': 2, 'is_player': False, 'max_distance_from_start_location': 1000000, 'max_wearable_items': 3, 'max_wieldable_items': 1, 'mission': '', 'movement_energy_cost': 0, 'name': 'prisoner', 'name_prefix': '', 'names': ['prisoner'], 'node_id': 'prisoner_1', 'num_wearable_items': 0, 'num_wieldable_items': 0, 'object': False, 'on_events': [], 'pacifist': False, 'persona': '', 'quests': [], 'size': 20, 'speed': 5, 'strength': 0, 'tags': [], 'usually_npc': False}, 'torturer_1': {'agent': True, 'aggression': 0, 'attack_taggedAgents': [], 'blocked_by': {}, 'blocking': None, 'char_type': 'person', 'classes': ['agent'], 'contain_size': 0, 'contained_nodes': {}, 'container_node': {'target_id': 'Dungeon_1'}, 'damage': 1, 'db_id': None, 'dead': False, 'defense': 0, 'desc': '', 'dexterity': 0, 'dont_accept_gifts': False, 'followed_by': {}, 'follow': None, 'food_energy': 1, 'health': 2, 'is_player': False, 'max_distance_from_start_location': 1000000, 'max_wearable_items': 3, 'max_wieldable_items': 1, 'mission': '', 'movement_energy_cost': 0, 'name': 'torturer', 'name_prefix': '', 'names': ['torturer'], 'node_id': 'torturer_1', 'num_wearable_items': 0, 'num_wieldable_items': 0, 'object': False, 'on_events': [], 'pacifist': False, 'persona': '', 'quests': [], 'size': 20, 'speed': 5, 'strength': 0, 'tags': [], 'usually_npc': False}, 'chains_1': {'agent': False, 'classes': ['object'], 'contain_size': 0, 'contained_nodes': {}, 'container': False, 'container_node': {'target_id': 'Dungeon_1'}, 'db_id': None, 'dead': False, 'desc': '', 'drink': False, 'equipped': None, 'food': False, 'food_energy': 0, 'gettable': True, 'locked_edge': None, 'name': 'chains', 'name_prefix': '', 'names': ['chains'], 'node_id': 'chains_1', 'object': True, 'on_use': None, 'room': False, 'size': 1, 'stats': {'damage': 0, 'defense': 0}, 'surface_type': 'on', 'value': 1, 'wearable': False, 'wieldable': False}, 'chair_1': {'agent': False, 'classes': ['object'], 'contain_size': 0, 'contained_nodes': {}, 'container': False, 'container_node': {'target_id': 'Dungeon_1'}, 'db_id': None, 'dead': False, 'desc': '', 'drink': False, 'equipped': None, 'food': False, 'food_energy': 0, 'gettable': True, 'locked_edge': None, 'name': 'chair', 'name_prefix': '', 'names': ['chair'], 'node_id': 'chair_1', 'object': True, 'on_use': None, 'room': False, 'size': 1, 'stats': {'damage': 0, 'defense': 0}, 'surface_type': 'on', 'value': 1, 'wearable': False, 'wieldable': False}}, 'agents': ['prisoner_1', 'torturer_1'], 'objects': ['chains_1', 'chair_1'], 'rooms': ['Dungeon_1']}}
target_room = args["target_room"]
room_graph = args["room_graph"]
original_rooms = room_graph['rooms']
room_graph['rooms'] = [r.replace(" ", "_") for r in room_graph['rooms']]
room_graph['objects'] = [r.replace(" ", "_") for r in room_graph['objects']]
room_graph['agents'] = [r.replace(" ", "_") for r in room_graph['agents']]

# cur_room = room_graph['rooms']
cur_room = target_room.replace(" ", "_")
room_graph['rooms'] = [cur_room]
cur_room = target_room.replace(" ", "_")

print(f"cur_room {cur_room}")
converted_graph = get_room_content_from_json(room_graph)
print(f"converted graph")
print(converted_graph)

graph = world_builder_agent.add_room_description(converted_graph)
graph = world_builder_agent.add_room_backstory(graph)
print(f"Adding description: {graph['description']}")
print(f"Adding backstory: {graph['background']}")
room_graph = modify_room_attrs(room_graph, cur_room, "desc", graph["description"])
room_graph = modify_room_attrs(room_graph, cur_room, "extra_desc", graph["background"])

# final step, fix the room list
room_graph['rooms'] = original_rooms
print(room_graph)