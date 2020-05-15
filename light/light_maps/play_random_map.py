#!/usr/bin/env python3
from parlai_internal.projects.light.light_maps.build_map import BuildLightMap


def run_graph(g, agent_name):
    use_graph = g
    use_graph.get_text(agent_name).rstrip('\n')
    use_graph.parse_exec(agent_name, 'look')
    print(use_graph.get_text(agent_name).rstrip('\n'))
    while True:
        act = input('action> ')
        if act == '':
            continue
        if act == 'exit':
            print('Exiting graph run')
            return
        elif act in ['new', 'reset']:
            print('A mist fills the world and everything resets')
            use_graph = BuildLightMap(debug=False).get_graph()
            use_graph.get_text(agent_name).rstrip('\n')
            use_graph.parse_exec(agent_name, 'look')
            print(use_graph.get_text(agent_name).rstrip('\n'))
        else:
            status, c_acts_text = use_graph.parse_exec(agent_name, act)
            if status:
                use_graph.update_world()
            print(use_graph.get_text(agent_name).rstrip('\n'))


g = BuildLightMap(debug=False).get_graph()
run_graph(g, 'player')
