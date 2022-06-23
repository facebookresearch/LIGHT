import light.modeling.tasks.common_sense.constants as consts
import random

def get_item_class(item_data):
    if 'room' in item_data and item_data['room']:
        return consts.ElementType.ROOM
    elif item_data['object']:
        return consts.ElementType.OBJECT
    elif item_data['agent']:
        return consts.ElementType.CHARACTER
    else:
        raise ValueError(f'Invalid item type. Item details {item_data}')

def get_room_content_from_json(graph_dict):
    """
    Generates game state tuples for the given state graph.
    """

    # graph_dict = json.loads(json_graph)
    content = {'objects': [], 'characters': []}
    meta_params = {'db_id': 0}

    def add_item_to_graph(item_to_add, container_node_id=None, container_edge=None):
        """
        Adds nodes to the dictionary by BFS traversal of nodes tree.
        """
        print(f"ADDING: {item_to_add}")
        # Adding the item itself
        item_type = get_item_class(item_to_add)
        item_node_id = item_to_add['node_id']
        if item_type == consts.ElementType.ROOM:
            # Room setting
            content['setting'] = item_to_add['name']
            # Room description
            content['description'] = item_to_add['desc']
            # Room background
            content['background'] = item_to_add['extra_desc']
            content['db_id'] = meta_params['db_id']
            meta_params['db_id'] = meta_params['db_id'] + 1

        elif item_type == consts.ElementType.OBJECT:
            new_item = {
                'element_type': 'objects',
                'db_id': meta_params['db_id'],
            }
            meta_params['db_id'] = meta_params['db_id'] + 1
            for graph_name, edge_name, convert_to_float in (
                ('gettable', 'is_gettable', True),
                ('wearable', 'is_wearable', True),
                # ('wieldable', 'is_wieldable', True),
                ('wieldable', 'is_weapon', True),
                ('food', 'is_food', True),
                ('drink', 'is_drink', True),
                ('container', 'is_container', True),
                ('surface_type', 'is_surface', True),
                ('desc', 'description', False),
                ('name_prefix', 'name_prefix', False),
                ('name', 'name', False),
                ('node_id', 'node_id', False),
                (consts.SEEN_IN_TRAIN_DATA, consts.SEEN_IN_TRAIN_DATA, False),
                (consts.IS_IN_ROOM, consts.IS_IN_ROOM, False),
                ('contains_from_db', 'containing_objects', False),
            ):
                if graph_name == "surface_type":
                    new_item[edge_name] = False
                else:
                    if graph_name not in item_to_add:
                        new_item[edge_name] = 0 if convert_to_float else None
                        if graph_name == consts.IS_IN_ROOM:
                            new_item[edge_name] = True
                        elif graph_name == "contains_from_db":
                            new_item[edge_name] = []
                    else:
                        new_item[edge_name] = item_to_add[graph_name]
                if convert_to_float:
                    # convert bool to float which can then converted down the line to a binary str
                    original_value = new_item[edge_name]
                    converted = float(original_value)
                    new_item[edge_name] = converted
            if container_node_id is None:
                content['objects'].append(new_item)
            else:
                for o in content['objects']:
                    if o['node_id'] == container_node_id:
                        o[container_edge] = o.get(container_edge, [])
                        # o[container_edge].append(new_item)
                        o[container_edge].append(new_item['name'])
                        break
                else:
                    for c in content['characters']:
                        if c['node_id'] == container_node_id:
                            c[container_edge] = c.get(container_edge, [])
                            c[container_edge].append(new_item)
                            break

        elif item_type == consts.ElementType.CHARACTER:
            new_item = {
                'element_type': 'characters',
                consts.IS_IN_ROOM: True,
                'db_id': meta_params['db_id'],
            }
            meta_params['db_id'] = meta_params['db_id'] + 1
            for graph_name, edge_name in (
                ('dead', consts.GraphEdges.IS_DEAD),
                ('damage', consts.GraphEdges.HAS_DAMAGE_LEVEL),
                ('health', consts.GraphEdges.HAS_HEALTH_LEVEL),
                ('strength', consts.GraphEdges.HAS_STRENGTH_LEVEL),
                ('desc', 'desc'),
                ('persona', 'persona'),
                ('name_prefix', 'name_prefix'),
                ('name', 'name'),
                ('node_id', 'node_id'),
                (consts.SEEN_IN_TRAIN_DATA, consts.SEEN_IN_TRAIN_DATA),
            ):
                if graph_name not in item_to_add:
                    new_item[edge_name] = None
                else:
                    new_item[edge_name] = item_to_add[graph_name]
            
            if container_node_id is None:
                content['characters'].append(new_item)
            else:
                for o in content['objects']:
                    if o['node_id'] == container_node_id:
                        o[container_edge] = o.get(container_edge, [])
                        o[container_edge].append(new_item)
                        break
                else:
                    for c in content['characters']:
                        if c['node_id'] == container_node_id:
                            c[container_edge] = c.get(container_edge, [])
                            c[container_edge].append(new_item)
                            break

        # Recursively adding the objects under a component
        for sub_comps in item_to_add['contained_nodes']:
            sub_comp_node = graph_dict['nodes'][sub_comps]
            if item_type == consts.ElementType.ROOM:
                sub_com_type = get_item_class(sub_comp_node)
                if (
                    sub_com_type == consts.ElementType.OBJECT
                    or sub_com_type == consts.ElementType.CHARACTER
                ):
                    add_item_to_graph(sub_comp_node)
                continue
            elif item_type == consts.ElementType.OBJECT:
                add_item_to_graph(
                    sub_comp_node,
                    container_node_id=item_node_id,
                    container_edge="containing_objects",
                )
                continue
            else:  # Item belongs to a character
                equipped_type = sub_comp_node.get('equipped')
                if not equipped_type:
                    add_item_to_graph(
                        sub_comp_node,
                        container_node_id=item_node_id,
                        container_edge="carrying_objects",
                    )
                    continue

                if equipped_type == 'equip':
                    # Handling unclarified equipped items
                    assert (
                        sub_comp_node['wearable'] or sub_comp_node['wieldable']
                    ), 'Equipped unequipable item.'
                    if sub_comp_node['wearable'] and sub_comp_node['wieldable']:
                        equipped_type = 'wear_wield'
                    elif sub_comp_node['wearable']:
                        equipped_type = 'wear'
                    elif sub_comp_node['wieldable']:
                        equipped_type = 'wield'

                if equipped_type == 'wear_wield':
                    add_item_to_graph(
                        sub_comp_node,
                        container_node_id=item_node_id,
                        container_edge="wearing_objects",
                    )
                    add_item_to_graph(
                        sub_comp_node,
                        container_node_id=item_node_id,
                        container_edge="wielding_objects",
                    )
                elif equipped_type == 'wear':
                    add_item_to_graph(
                        sub_comp_node,
                        container_node_id=item_node_id,
                        container_edge="wearing_objects",
                    )
                elif equipped_type == 'wield':
                    add_item_to_graph(
                        sub_comp_node,
                        container_node_id=item_node_id,
                        container_edge="wielding_objects",
                    )
                else:
                    ValueError(f'Object with invalid equipped type "{equipped_type}".')

    rooms = graph_dict['rooms']
    assert len(rooms) == 1, f'Common sense teacher is currently only handling one room.'
    # Adding the room, and recursively anything underneath it.
    add_item_to_graph(graph_dict['nodes'][rooms[0]], 0)
    return content

########################################################################################
# reverse graph to old_format
########################################################################################

def modify_room_attrs(input_graph, room_name, attr_name, attr_value):
    input_graph['nodes'][room_name][attr_name] = attr_value
    return input_graph

def add_character_secondary_objects_to_graph(input_graph, node_id, carried, wielded, worn):
    for o in carried:
        if type(o) is str:
            o = {'name':o}
        o_id = o['name'] + "_x"
        new_node = {
            "agent": False,
            "classes": ["object"],
            "contain_size": 20,
            "contained_nodes": {},
            "container": True,
            "container_node": {
                "target_id": node_id
                },
            "db_id": None,
            "dead": False,
            "desc": o.get('description', ''),
            "drink": False,
            "equipped": None,
            "food": False,
            "food_energy": 0,
            "gettable": False,
            "locked_edge": None,
            "name": o,
            "name_prefix": "a",
            "names": [o],
            "node_id": o_id,
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
            "wieldable": False,
            "from_model": True
        }
        # input_graph['objects'].append(new_node)
        input_graph['objects'].append(o_id)
        input_graph['nodes'][o_id] = new_node
        input_graph['nodes'][node_id]['contained_nodes'][o_id] = {"target_id": o_id}
    
    for o in wielded:
        if type(o) is str:
            o = {'name':o}
        o_id = o['name'] + "_x"
        new_node = {
            "agent": False,
            "classes": ["object"],
            "contain_size": 20,
            "contained_nodes": {},
            "container": True,
            "container_node": {
            "target_id": node_id
            },
            "db_id": None,
            "dead": False,
            "desc": o.get('description', ''),
            "drink": False,
            "equipped": None,
            "food": False,
            "food_energy": 0,
            "gettable": False,
            "locked_edge": None,
            "name": o,
            "name_prefix": "a",
            "names": [o],
            "node_id": o_id,
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
            "wieldable": True,
            "from_model": True
        }
        # input_graph['objects'].append(new_node)
        input_graph['objects'].append(o_id)
        input_graph['nodes'][o_id] = new_node
        input_graph['nodes'][node_id]['contained_nodes'][o_id] = {"target_id": o_id}

    for o in worn:
        if type(o) is str:
            o = {'name':o}
        o_id = o['name'] + "_x"
        new_node = {
            "agent": False,
            "classes": ["object"],
            "contain_size": 20,
            "contained_nodes": {},
            "container": True,
            "container_node": {
            "target_id": node_id
            },
            "db_id": None,
            "dead": False,
            "desc": o.get('description', ''),
            "drink": False,
            "equipped": None,
            "food": False,
            "food_energy": 0,
            "gettable": False,
            "locked_edge": None,
            "name": o,
            "name_prefix": "a",
            "names": [o],
            "node_id": o_id,
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
            "wearable": True,
            "wieldable": False,
            "from_model": True
        }
        # input_graph['objects'].append(new_node)
        input_graph['objects'].append(o_id)
        input_graph['nodes'][o_id] = new_node
        input_graph['nodes'][node_id]['contained_nodes'][o_id] = {"target_id": o_id}
    return input_graph

def add_character_to_graph(input_graph, room_name, character_dict):
    node_id = character_dict['name'] + "_x"
    print(f"Adding character: {node_id}")
    print(character_dict)

    carried = character_dict.get('carrying_objects', [])
    wielded = character_dict.get('wielding_objects', [])
    worn = character_dict.get('wearing_objects', [])

    input_graph = add_character_secondary_objects_to_graph(input_graph, node_id, carried, wielded, worn)

    all_contained = [*carried, *wielded, *worn]
    contained_nodes = {o+"_x":{"target_id":o+"_x"} for o in all_contained}
    new_node = {
        "agent": True,
        "aggression": 0,
        "pacifist": False,
        "char_type": "creature",
        "classes": ["agent"],
        "contain_size": 20,
        "contained_nodes": contained_nodes,
        "container_node": {
          "target_id": room_name
        },
        "damage": 1,
        "db_id": None,
        "defense": 0,
        "desc": character_dict.get('desc', ''),
        "followed_by": {},
        "following": None,
        "food_energy": 1,
        "health": 5,
        "is_player": False,
        "name": character_dict['name'],
        "name_prefix": "a",
        "names": [character_dict['name']],
        "tags": [],
        "node_id": node_id,
        "object": False,
        "on_events": None,
        "persona": character_dict.get('persona', ''),
        "room": False,
        "size": 20,
        "speed": 20,
        "from_model": True
    }
    
    input_graph['nodes'][node_id] = new_node
    input_graph['nodes'][room_name]['contained_nodes'][node_id] = {"target_id": node_id}
    input_graph['agents'].append(node_id)
    return input_graph

def add_object_secondary_objects_to_graph(input_graph, node_id, contained):
    for o in contained:
        o_id = o + "_x"
        new_node = {
            "agent": False,
            "classes": ["object"],
            "contain_size": 20,
            "contained_nodes": {},
            "container": True,
            "container_node": {
            "target_id": node_id
            },
            "db_id": None,
            "dead": False,
            "desc": '',
            "drink": False,
            "equipped": None,
            "food": False,
            "food_energy": 0,
            "gettable": False,
            "locked_edge": None,
            "name": o,
            "name_prefix": "a",
            "names": [o],
            "node_id": o_id,
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
            "wieldable": False,
            "from_model": True
        }
        input_graph['objects'].append(o_id)
        input_graph['nodes'][o_id] = new_node
        input_graph['nodes'][node_id]['contained_nodes'][o_id] = {"target_id": o_id}
        # input_graph['objects'].append(new_node)
    return input_graph

def add_object_to_graph(input_graph, room_name, object_dict):
    node_id = object_dict['name'] + "_x"
    print(f"Adding object: {node_id}")
    print(object_dict)
    contained = object_dict.get('containing_objects', [])
    input_graph = add_object_secondary_objects_to_graph(input_graph, node_id, contained)

    new_node = {
        "agent": False,
        "classes": ["object"],
        "contain_size": 20,
        "contained_nodes": {o+"_x":{"target_id":o+"_x"} for o in object_dict.get('containing_objects', [])},
        "container": True,
        "container_node": {
          "target_id": room_name
        },
        "db_id": None,
        "dead": False,
        "desc": object_dict.get('description'),
        "drink": False,
        "equipped": None,
        "food": False,
        "food_energy": 0,
        "gettable": False,
        "locked_edge": None,
        "name": object_dict['name'],
        "name_prefix": "a",
        "names": [object_dict['name']],
        "node_id": node_id,
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
        "wieldable": False,
        "from_model": True
      }
    
    input_graph['nodes'][node_id] = new_node
    input_graph['objects'].append(node_id)
    input_graph['nodes'][room_name]['contained_nodes'][node_id] = {"target_id": node_id}
    return input_graph

########################################################################################
# helpers to create objects using intermediary graph
########################################################################################

def run_create_char_or_objs(graph, agent, name="characters", count=1):
    # name can be characters or objects
    original_items = set([c["name"] for c in graph[name]])
    adder_method = agent.add_character if name == "characters" else agent.add_object
    
    new_graph = adder_method(graph, count=count)
    new_items = set([c["name"] for c in new_graph[name]])
    
    item_diff = [c for c in new_items if c not in original_items]

    attr_method = agent.add_all_character_attributes if name == "characters" else agent.add_all_object_attributes
    for c in item_diff:
        new_graph = attr_method(new_graph, c)

    return new_graph, item_diff

def run_create_char(graph, agent, count=1):
    return run_create_char_or_objs(graph, agent, name="characters", count=count)

def run_create_obj(graph, agent, count=1):
    return run_create_char_or_objs(graph, agent, name="objects", count=count)

########################################################################################
# just for creating nice looking graph printouts
########################################################################################

def clean_str(txt):
    # ensure txt is str, could be int/float
    txt = str(txt)
    for char in ('\n', '\t'):
        txt = txt.replace(char, ' ')
    return txt

def graph_state_tuple(v1, v2, edge):
    edge_name = edge if isinstance(edge, str) else edge.name
    return consts.GRAPH_TUPLES_DELIM.join([clean_str(v1), edge_name, clean_str(v2)])

def replace_binarized_attributes_with_description(states_str: str):
    if states_str == consts.GraphMutations.NO_MUTATION.name:
        return states_str

    states = states_str.split(consts.GRAPH_STATES_DELIM)
    for st_id in range(len(states)):
        curr_state = states[st_id]

        if 'HAD_ACTED' in curr_state:
            # Game action history
            continue

        v1, e, v2 = curr_state.split(consts.GRAPH_TUPLES_DELIM)
        if e not in consts.ATTRIBUTE_VALUES:
            continue

        # Replacing binarized state with their equivalent text
        assert v2 in (
            '0',
            '1',
        ), f'unsupported binary value {v2} for {e}'
        attribute_text_equivalent = random.choice(consts.ATTRIBUTE_VALUES[e][int(v2)])
        states[st_id] = graph_state_tuple(
            v1, attribute_text_equivalent, consts.GraphEdges.HAS_ATTRIBUTE
        )

    return consts.GRAPH_STATES_DELIM.join(states)