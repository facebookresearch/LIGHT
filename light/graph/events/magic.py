import random
import json
from light.graph.elements.graph_nodes import (
    GraphAgent,
    GraphNode,
)
import os.path
from light.graph.events.base import TriggeredEvent
from light.graph.events.graph_events import ArriveEvent, LeaveEvent, LookEvent

magic_db = None


def init_magic(datapath):
    global magic_db
    if datapath is not None and len(datapath) > 0:
        files = datapath.split(',')
        magic_db = []
        for f in files:
            if not os.path.exists(datapath):
                print(f"Warning - no magic file at {datapath}, skipping!")
                continue
            with open(f, "r") as jsonfile:
                mdb = json.load(jsonfile)
                magic_db = magic_db + mdb
        print("[ loaded " + str(len(magic_db)) + " magic items]")


def mort(agent, event):
    pass


class CreationEvent(TriggeredEvent):
    def view_as(self, viewer: GraphAgent):
        """Provide the way that the given viewer should view this event"""
        if self.item_name is None:
            # Nothing happened.
            if viewer == self.actor:
                return "Nothing seems to happen."
            return
        text = (
            "Zap! A mighty roar sounds! Out of thin air, "
            + self.item_name 
            + " appears!"
        )
        if viewer == self.actor:
            return "You wave your hands around as you chant the words. " + text
        else:
            return text

    def to_canonical_form(self) -> str:
        """return action text for equipping the object"""
        # TODO: not sure how to do this.
        return "create TODO"

def add_room(g, curr_room, new_room):
    # find a possible path to connect to the new room, and connect
    p1 = curr_room.grid_location
    directions = ['north', 'south', 'east', 'west']
    oppd = {'north':'south', 'south':'north','east':'west','west':'east'}
    random.shuffle(directions)
    for d in directions:
        exists = False
        for _, edge in curr_room.neighbors.items():
            if d in edge.label:
                exists = True
        if not exists:
            node = g.add_room(new_room["name"], new_room)
            p2 = [p1[0], p1[1], p1[2]]
            if d == 'north':
                p2[1] -= 1
            if d == 'south':
                p2[1] += 1
            if d == 'east':
                p2[0] += 1
            if d == 'west':
                p2[0] -= 1
            node.grid_location = p2
            g.add_paths_between(curr_room, node, 'a path to the ' + d, 'a path to the ' + oppd[d])            
            return True, ('a path to the ' + d)

    return False, ""

def find_item(txt, filter_type=None):
    obs = []
    txt = ' ' + txt.lower() + ' '
    for i in range(0, len(magic_db)):
        if txt in ' ' + magic_db[i]["name"].lower() + ' ':
            if filter_type is not None:
                if filter_type in magic_db[i]:
                    obs.append(i)
            else:
                obs.append(i)
    if len(obs) == 0:
        return {}
    else:
        obj = magic_db[random.choice(obs)]
        return obj


def creo(agent, event):
    # Test if this agent can cast a creation spell.
    can_cast = False
    for node in agent.target_node.get_contents():
        # TODO: later maybe make a proprty: hasattr(node, 'magical_create') and node.magical_create:
        if node.name == 'orb of creation':
            can_cast = True
    if agent.world.opt.get('allow_save_world', False):
        can_cast = True
    if not can_cast:
        return
    
    # creation location
    room = event.actor.get_room()
    world = agent.world
    g = agent.world.oo_graph
    query = event.text_content
    filter_type = None
    if query.startswith('creo device '):
        query = query.replace('creo device ', '')
        filter_type = 'is_object'
    elif query.startswith('creo loci '):
        query = query.replace('creo loci ', '')
        filter_type = 'is_room'
    elif query.startswith('creo creatura '):
        query = query.replace('creo creatura ', '')
        filter_type = 'is_character'
    else:
        query = query.replace('creo ', '')

    item = find_item(query, filter_type)
    new_event = CreationEvent(event.actor)
    new_event.actor = event.actor
    new_event.room = room
    new_event.item_name = None
    if item.get("is_object", False):
        node = g.add_object(item["name"], item)
        if event.actor.would_fit(node) and node.size == 1:
            node.force_move_to(event.actor)
        else:
            node.force_move_to(room)
        new_event.item_name = node.get_prefix_view()
    if item.get("is_character", False):
        node = g.add_agent(item["name"], item)
        node.force_move_to(room)
        new_event.item_name = node.get_prefix_view()
        world.purgatory.fill_soul(node)
    if item.get("is_room", False):
        success, view_text = add_room(g, room, item)
        if success:
            new_event.item_name = view_text
        
    agent.world.broadcast_to_room(new_event)

def teleport(agent, event):
    # Test if this agent can cast a teleport spell.
    can_cast = False
    for node in agent.target_node.get_contents():
        if node.name == 'dark emerald ring':
            can_cast = True
    if agent.world.opt.get('allow_save_world', False):
        can_cast = True
    if not can_cast:
        return

    room = event.actor.get_room()
    world = agent.world
    g= world.oo_graph
    found_node = None
    query = event.text_content.lower().replace('locus ','')
    for _, node in g.all_nodes.items():
        if query in node.name.lower():
            found_node = node
            break
    if found_node is not None:
        new_room = found_node.get_room()
        LeaveEvent(event.actor, [g.void]).execute(world)
        event.actor.move_to(new_room)
        ArriveEvent(event.actor, text_content="arrived in a puff of smoke!").execute(world)
        LookEvent(event.actor).execute(world)
    else:
        # nothing happens event
        new_event = CreationEvent(event.actor)
        new_event.actor = event.actor
        new_event.room = room
        new_event.item_name = None        
    
    
def save(agent, event):
    print("[saving world state!!!]")
    g = agent.world.oo_graph
    data = g.to_json()
    # turn off is_player feature:
    data =  data.replace('"is_player": true', '"is_player": false')
    fw = open('/tmp/map.json', 'w')
    fw.write(data)
    fw.close()

def check_if_cast_magic_from_event(agent, event):
    event_name = event.__class__.__name__
    if event_name == "SayEvent" and event.actor == agent.target_node:
        if event.text_content == "creoservo" and agent.world.opt.get('allow_save_world', False):
            save(agent, event)
        if event.text_content.startswith("creo "):
            creo(agent, event)
        if event.text_content.startswith("mort "):
            mort(agent, event)
        if event.text_content.startswith("locus "):
            teleport(agent, event)
