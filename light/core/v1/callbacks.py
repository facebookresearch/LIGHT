#!/usr/bin/env python3
debug = False


def write_text(g, callback_args, graph_args):
    text = callback_args[0]
    petter = graph_args[0]
    place_id = g.location(petter)
    g.send_action(petter, {
        'caller': None,
        'room_id': place_id,
        'txt': text,
    })


def use_with(g, callback_args, graph_args):
    '''Attempts to process a use based on the use's set paramaters. Returns
    true if the use was handled in any way, false if nothing occurred and no
    messages were sent'''
    actor_id = graph_args[0]
    held_item = graph_args[1]
    other_item = graph_args[2]

    # Is this the right held item?
    if g.node_to_desc_raw(held_item) not in callback_args['held_item']:
        return None
    # Can it be used with the other item?
    if g.node_to_desc_raw(other_item) not in callback_args['other_item']:
        return None

    both_held = callback_args.get('both_held', True)
    if both_held and g.node_contained_in(other_item) != actor_id:
        # Both are not held even though it is required
        g.send_msg(actor_id, 'You have to have both first. ')
        # Return True as this is technically 'handled'
        return False

    room_id = g.location(actor_id)

    desc_1 = g.node_to_desc(held_item, use_the=True)
    desc_2 = g.node_to_desc(other_item, use_the=True)
    action_description = callback_args['output_text'].format(desc_1, desc_2)

    consume_item_1 = callback_args.get('destroy_1', True)
    consume_item_2 = callback_args.get('destroy_2', True)
    if consume_item_1:
        g.delete_node(held_item)
    if consume_item_2:
        g.delete_node(other_item)

    use_with_action = {'caller': 'use', 'name': 'used_with',
                       'room_id': room_id, 'actors': [actor_id],
                       'add_descs': [action_description]}

    for new_node in callback_args.get('products'):
        target = room_id if new_node.get('dropped', False) else actor_id
        created_instances = {
            'target': g.parser.create_instance(new_node['class'])
        }
        created_instances['target']['id'] = g.parser.add_instance_to_graph(
            g, created_instances['target']
        )
        g.move_object(created_instances['target']['id'], target)
        instance = created_instances['target']
        if 'contains' in instance:
            for contained_wrap in instance['contains']:
                contained_wrap['is_created'] = False
        while g.parser.instances_need_expanding(created_instances):
            created_instances = g.parser.expand_instances(g, created_instances)

    g.broadcast_to_room(use_with_action)
    return True


callbacks = {'write_text': write_text, 'use_with': use_with}


def handle(graph, in_cbs, args):
    rets = []
    for callback in in_cbs:
        rets.append(callbacks[callback['name']](graph, callback['args'], args))
    return rets


ACT_TO_TRIGGER_MAPS = {
    # List of actions to triggers, with a mapping of where that trigger pulls
    # the arguments from in the original action
    'look': {'looks': [0]},
    'eat': {'eats': [0, 1]},
    'give': {'receives': [2, 1], 'moves_to': [1, 2], 'moves_from': [1, 0],
             'gives': [0, 2, 1]},
    'get': {'moves_to': [1, 0], 'moves_from': [1, 2], 'gets': [0, 1]},
    'steal': {'moves_to': [1, 0], 'moves_from': [1, 2],
              'steals': [0, 1, 2]},
    'go': {'moves_to': [0, 1], 'moves_from': [0, 0]},
    'hit': {'hits': [0, 1]},
    'drink': {'drinks': [0, 1]},
    'tell': {'tell': [0, 1, 2]},
    'miss': {'misses': [0, 1]},
    'examine': {'examines': [0, 1]},
    'say': {'say': [0, 1]},
    'shout': {'shout': [0, 1]}
}


def evaluate_constraint(constraint, g, a, v):
    if constraint == 'attribute_value_greater':
        return g.get_prop(a[0], a[1]) > a[2]
    elif constraint == 'attribute_value_less':
        return g.get_prop(a[0], a[1]) > a[2]
    elif constraint == 'attribute_value_equal':
        return g.get_prop(a[0], a[1]) == a[2]
    elif constraint == 'attribute_value_true':
        return g.get_prop(a[0], a[1]) is True
    elif constraint == 'attribute_value_false':
        return g.get_prop(a[0], a[1], False) is False
    elif constraint == 'variable_greater':
        return v[a[0]] > a[1]
    elif constraint == 'variable_less':
        return v[a[0]] < a[1]
    elif constraint == 'variable_equal':
        return v[a[0]] == a[1]
    elif constraint == 'variable_true':
        return v[a[0]] is True
    elif constraint == 'variable_false':
        return v[a[0]] is False
    elif constraint == 'has_class':
        return a[1] in g.get_prop(a[0], 'classes')
    elif constraint == 'is_in':
        return g.location(a[0]) == a[1]


def do_action(action, g, a, v):
    if action == 'increment_variable':
        v[a[0]] += a[1]
    elif action == 'decrement_variable':
        v[a[0]] -= a[1]
    elif action == 'increment_attribute':
        val = g.get_prop(a[0], a[1], 0) + a[2]
        g.set_prop(a[0], a[1], val)
    elif action == 'decrement_attribute':
        val = g.get_prop(a[0], a[1], 0) - a[2]
        g.set_prop(a[0], a[1], val)
    elif action == 'set_attribute':
        g.set_prop(a[0], a[1], a[2])
    elif action == 'set_variable':
        v[a[0]] = a[1]
    elif action == 'tell':
        g.send_msg(a[0], a[1].strip() + ' ')
    elif action == 'broadcast':
        if 'room' in g.get_prop(a[0], 'classes'):
            msg_action = {
                'caller': None,
                'room_id': a[0],
                'txt': a[1],
            }
            g.broadcast_to_room(msg_action)
        else:
            msg_action = {
                'caller': None,
                'room_id': g.room(a[0]),
                'txt': a[1],
            }
            g.broadcast_to_room(msg_action, exclude_agents=[a[0]])
    elif action == 'create':
        created_instances = {
            'target': g.parser.create_instance(a[0])
        }
        created_instances['target']['id'] = g.parser.add_instance_to_graph(
            g, created_instances['target']
        )
        g.move_object(created_instances['target']['id'], a[1])
        instance = created_instances['target']
        if 'contains' in instance:
            for contained_wrap in instance['contains']:
                contained_wrap['is_created'] = False
        while g.parser.instances_need_expanding(created_instances):
            created_instances = g.parser.expand_instances(g, created_instances)
    elif action == 'delete':
        g.delete_node(a[0])
    elif action == 'move':
        g.move_object(a[0], a[1])
    elif action == 'follow':
        g.set_follow(a[0], a[1])


def extract_arg(graph, prepped_args, arg):
    if arg['type'] == 'argument':
        return prepped_args[arg['value']]
    elif arg['type'] == 'location':
        return graph.room(arg['contents']['value'])
    elif arg['type'] == 'object':
        return arg['contents']
    elif arg['type'] == 'str_iter':
        i = arg['value']['iter']
        arg['value']['iter'] = (i + 1) % len(arg['value']['data'])
        return arg['value']['data'][i]
    else:
        return arg['value']


def clean_word(word):
    return word.strip('.').strip('?').strip('!').strip(',')


def score_overlap(t1, t2):
    t1_words_bad = t1.lower().split(' ')
    t1_words = [clean_word(t) for t in t1_words_bad]
    t2_words_bad = t2.lower().split(" ")
    t2_words = [clean_word(t) for t in t2_words_bad]
    while ['the'] in t1_words:
        t1_words.remove('the')
    while ['the'] in t2_words:
        t2_words.remove('the')
    denom = len(t1_words) + len(t2_words)
    if denom == 0:
        return 0
    num = 0
    for t1_word in t1_words:
        if t1_word in t2_words:
            num += 2
        elif t1_word[:-1] in t2_words:
            num += 2
    return num / denom


def text_match(text, triggers, threshold=0):
    best_score = threshold
    best_match = None
    for trigger in triggers:
        match_array = trigger['matches']
        for match_value in match_array:
            if type(match_value) is dict:
                match_value = match_value['value']
            score = score_overlap(text, match_value)
            if score > best_score:
                best_score = score
                best_match = trigger
    return best_match


def spacing_fix(text):
    error_list = [
        (' .', '.'),
        (' !', '!'),
        (' ?', '?'),
        (' ,', ','),
        (" '", "'"),
        (' d ', "'d '"),
        (' ve ', "'ve '"),
        (' re ', "'re '"),
        (' i ', " I '"),
    ]
    for tup in error_list:
        text = text.replace(tup[0], tup[1])
    return text


def handle_dialogue_callback(callback, use_args, graph, variables):
    sub_triggers = callback['trigger']['sub_triggers']
    triggers = sub_triggers['match']

    tell_val = 0.5
    say_val = 0.7

    if len(use_args) > 2:  # tell
        model_name = graph.get_prop(use_args[1], 'ml_model', None)
        if model_name is None:
            tell_val = 0.1
        rank_match = text_match(use_args[2], triggers, tell_val)
    else:                  # say
        rank_match = text_match(use_args[1].strip('"'), triggers, say_val)
    if rank_match is not None:
        for action in rank_match['actions']:
            act_args = [
                extract_arg(graph, use_args, x) for x in action['args']
            ]
            do_action(action['type'], graph, act_args, variables)
        return True
    if sub_triggers.get('default', None) is None:
        return False
    if len(use_args) > 2:  # only use default on tells
        model_name = graph.get_prop(use_args[1], 'ml_model', None)
        if model_name in graph._models:
            graph._models[model_name].observe({
                'id': 'LIGHT',
                'text': use_args[2],
                'episode_done': False,
            })
            next_act_out = graph._models[model_name].act()
            next_act = spacing_fix(next_act_out['text']).strip()
            speaker = graph.node_to_desc(use_args[1]).capitalize()
            text = '{} said "{}"'.format(speaker, next_act.capitalize())
            graph.send_msg(use_args[0], text + ' ')
            return True
    for action in sub_triggers['default']:
        act_args = [
            extract_arg(graph, use_args, x) for x in action['args']
        ]
        do_action(action['type'], graph, act_args, variables)
    return True


def try_trigger_failed_parse_callback(callback, actor_id, text_input, graph,
                                      variables):
    for constraint in callback['constraints']:
        con_args = [
            extract_arg(graph, [actor_id], x) for x in constraint['args']
        ]
        if not evaluate_constraint(constraint['type'], graph,
                                   con_args, variables):
            return False

    sub_triggers = callback['trigger']['sub_triggers']
    triggers = sub_triggers['match']
    rank_match = text_match(text_input, triggers, 0.66)
    if rank_match is not None:
        for action in rank_match['actions']:
            act_args = [
                extract_arg(graph, [actor_id], x) for x in action['args']
            ]
            do_action(action['type'], graph, act_args, variables)
        return True
    if sub_triggers.get('default', None) is not None:
        for action in sub_triggers['default']:
            act_args = [
                extract_arg(graph, [actor_id], x) for x in action['args']
            ]
            do_action(action['type'], graph, act_args, variables)
        return True
    return False


def is_callback_triggered(callback, calling_func, variables, graph, arguments):
    if not calling_func.get_name() in ACT_TO_TRIGGER_MAPS:
        return False
    target_triggers = ACT_TO_TRIGGER_MAPS[calling_func.get_name()]
    trigger_func = callback['trigger']['trigger_func']
    if trigger_func not in target_triggers:
        return False
    arg_map = target_triggers[trigger_func]
    if trigger_func in ['tell', 'say', 'shout']:
        arg_map = arg_map[:-1]  # haven't yet parsed the text
    use_args = [arguments[idx] for idx in arg_map]
    if calling_func.get_name() == 'go' and trigger_func == 'moves_from':
        use_args[1] = graph.location(use_args[1])

    for idx, trigger_arg in enumerate(callback['trigger']['args']):
        if trigger_arg['type'] == 'instance' and \
                trigger_arg['value'] != use_args[idx]:
            return False
        elif trigger_arg['type'] == 'class' and trigger_arg['value'] not in \
                graph.get_prop(use_args[idx], 'classes'):
            return False
        elif trigger_arg['type'] == 'location':
            loc = graph.location(trigger_arg['contents']['value'])
            if use_args[idx] != loc:
                return False
    for constraint in callback['constraints']:
        con_args = [
            extract_arg(graph, use_args, x) for x in constraint['args']
        ]
        if not evaluate_constraint(constraint['type'], graph,
                                   con_args, variables):
            return False
    return True


def try_trigger_callback(callback, calling_func, variables, graph, arguments):
    if not calling_func.get_name() in ACT_TO_TRIGGER_MAPS:
        return False
    target_triggers = ACT_TO_TRIGGER_MAPS[calling_func.get_name()]
    trigger_func = callback['trigger']['trigger_func']
    if trigger_func not in target_triggers:
        return False
    use_args = [arguments[idx] for idx in target_triggers[trigger_func]]
    if calling_func.get_name() == 'go' and trigger_func == 'moves_from':
        use_args[1] = graph.location(use_args[1])
    for idx, trigger_arg in enumerate(callback['trigger']['args']):
        if trigger_arg['type'] == 'instance' and \
                trigger_arg['value'] != use_args[idx]:
            return False
        elif trigger_arg['type'] == 'class' and trigger_arg['value'] not in \
                graph.get_prop(use_args[idx], 'classes'):
            return False
        elif trigger_arg['type'] == 'location':
            loc = graph.location(trigger_arg['contents']['value'])
            if use_args[idx] != loc:
                return False
    for constraint in callback['constraints']:
        con_args = [
            extract_arg(graph, use_args, x) for x in constraint['args']
        ]
        if not evaluate_constraint(constraint['type'], graph,
                                   con_args, variables):
            return False
    if trigger_func in ['tell', 'say', 'shout']:
        return handle_dialogue_callback(callback, use_args, graph, variables)
    for action in callback['actions']:
        act_args = [
            extract_arg(graph, use_args, x) for x in action['args']
        ]
        do_action(action['type'], graph, act_args, variables)
    return True


def try_trigger_miss_callback(callback, variables, graph, arguments):
    target_triggers = ACT_TO_TRIGGER_MAPS['miss']
    trigger_func = callback['trigger']['trigger_func']
    if trigger_func not in target_triggers:
        return False
    use_args = [arguments[idx] for idx in target_triggers[trigger_func]]
    for idx, trigger_arg in enumerate(callback['trigger']['args']):
        if trigger_arg['type'] == 'instance' and \
                trigger_arg['value'] != use_args[idx]:
            return False
        elif trigger_arg['type'] == 'class' and trigger_arg['value'] not in \
                graph.get_prop(use_args[idx], 'classes'):
            return False
        elif trigger_arg['type'] == 'location':
            loc = graph.location(trigger_arg['contents']['value'])
            if use_args[idx] != loc:
                return False
    for constraint in callback['constraints']:
        con_args = [
            extract_arg(graph, use_args, x) for x in constraint['args']
        ]
        if not evaluate_constraint(constraint['type'], graph,
                                   con_args, variables):
            return False
    for action in callback['actions']:
        act_args = [
            extract_arg(graph, use_args, x) for x in action['args']
        ]
        do_action(action['type'], graph, act_args, variables)
    return True


def has_valid_override(calling_func, graph, arguments):
    callbacks = graph.callbacks
    variables = graph.variables
    for callback in callbacks.values():
        # Ensure this is the right function to be calling
        had_callback = is_callback_triggered(callback, calling_func, variables,
                                             graph, arguments)
        if had_callback:
            return callback['trigger']['override']
    return False


def try_overrides(calling_func, graph, arguments):
    callbacks = graph.callbacks
    variables = graph.variables
    for callback_name, callback in callbacks.items():
        # Ensure this is the right function to be calling
        had_callback = is_callback_triggered(callback, calling_func, variables,
                                             graph, arguments)
        if had_callback and not callback['trigger']['override']:
            return False  # A non-override takes precedence!
        had_callback = try_trigger_callback(callback, calling_func, variables,
                                            graph, arguments)
        if had_callback:
            if debug:
                print('Triggered ', callback_name)
            return True
    return False


def handle_callbacks(calling_func, graph, arguments):
    callbacks = graph.callbacks
    variables = graph.variables
    for callback in callbacks.values():
        if callback['trigger']['override']:
            continue
        had_callback = try_trigger_callback(callback, calling_func, variables,
                                            graph, arguments)
        if had_callback:
            return True
    return False


def handle_failed_parse_callbacks(fun_name, graph, arguments, actor_id):
    callbacks = graph.callbacks
    variables = graph.variables
    for callback in callbacks.values():
        if callback['trigger']['trigger_func'] != 'act_failed':
            continue
        text_input = fun_name + ' ' + ' '.join(arguments)
        had_callback = try_trigger_failed_parse_callback(
            callback, actor_id, text_input, graph, variables)
        if had_callback:
            return True
    return False


# Special case to handle callbacks coming from hit misses, as they don't have
# correct targets
def handle_miss_callbacks(calling_func, graph, arguments):
    callbacks = graph.callbacks
    variables = graph.variables
    for callback in callbacks.values():
        if callback['trigger']['override']:
            continue
        if callback['trigger']['trigger_func'] != 'misses':
            continue
        had_callback = try_trigger_miss_callback(callback, variables,
                                                 graph, arguments)
        if had_callback:
            return True
    return False
