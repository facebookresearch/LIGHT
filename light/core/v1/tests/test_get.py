#!/usr/bin/env python3
from parlai_internal.projects.light.v1.graph import *

def check(return_success, success, return_str, success_str):
    if return_str.rstrip(' ') != success_str:
        raise ValueError('FAILED on output msg:\n"' + str(return_str) +
                         '"\ninstead of:\n"' + success_str + '"')
    if success != return_success:
        raise ValueError('FAILED')
        
class Tests():
    def __init__(self):
        self.build_basic_world()
        
    def build_basic_world(self):
        opt = {}
        g = Graph(opt)
        self.g = g
        self.room_id = g.add_node('room1', {'classes':['room'], 'contain_size': 10000}, is_room=True)
        self.agent1_id = g.add_node('agent1', {'classes':['agent'], 'contain_size': 10})
        self.object1_id = g.add_node('object1', {'classes':['object'], 'size': 5})
        self.object2_id = g.add_node('object2', {'classes':['object'], 'size': 20})

        self.g.add_contained_in(self.agent1_id, self.room_id)
        self.g.add_contained_in(self.object1_id, self.room_id)
        self.g.add_contained_in(self.object2_id, self.room_id)
        
    def test_can_get(self):
        self.build_basic_world()
        success, action = self.g.parse_exec_internal(self.agent1_id, 'get object1')
        response = self.g._node_to_text_buffer[self.agent1_id]
        check(success, True, response, 'You got the object1.')
        print("response:" + str(response))

    def test_cant_get(self):
        self.build_basic_world()
        success, action = self.g.parse_exec_internal(self.agent1_id, 'get object2')
        response = self.g._node_to_text_buffer[self.agent1_id]
        print("response:" + str(response))
        # TODO: the engine should really say "this is too heavy to pick up",
        # but it says this right now:
        check(success, False, response, "You couldn't get the object2. You can't carry that much more.")


def main():
    print("[creating tests..]")
    t = Tests()
    t.test_can_get()
    t.test_cant_get()
    print("[..all done!]")


main()
