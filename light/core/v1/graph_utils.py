#!/usr/bin/env python3
def format_observation(self, graph, viewing_agent, action, telling_agent=None,
                       is_constraint=False):
    '''Return the observation text to display for an action'''
    use_actors = action['actors']
    if is_constraint:
        use_actors = use_actors[1:]
    descs = [graph.node_to_desc(a, from_id=action['room_id'], use_the=True)
             for a in use_actors]
    try:
        # Replace viewer with you
        i = use_actors.index(viewing_agent)
        descs[i] = 'you'
    except BaseException:
        pass

    if telling_agent is not None:
        try:
            # Replace telling agent with me or I depending
            i = use_actors.index(telling_agent)
            if i == 0:
                descs[0] = 'I'
            else:
                descs[i] = 'me'
        except BaseException:
            pass

    # Package descriptions and determine the format
    descs[0] = descs[0].capitalize()
    if 'add_descs' in action:
        descs += action['add_descs']
    if is_constraint:
        descs = [action['actors'][0]] + descs
    return self.get_action_observation_format(action, descs).format(*descs)
