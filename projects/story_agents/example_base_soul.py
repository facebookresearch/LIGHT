#!/usr/bin/env python3

from light.world.souls.soul import Soul


class ExampleBaseSoul(Soul):
    async def observe_event(self, event: "GraphEvent"):
        """
        All souls should define some kind of behavior for when an event occurs,
        ensuring that they are able to handle it somehow.

        The soul may choose to ask the world for possible actions it may take, and
        then take one in response, or perhaps bide its time, launching a thread
        to do something later. Maybe it just takes a note for itself.

        This method will always be called asyncronously, such that it can be
        cancelled and won't block execution of the world.
        """
        print(f"I, {self.target_node}, observed an event!", event)
        print(f"In this function, I can react to it however I want")
        print(f"I could even trigger a `self.world.parse_exec` if I wanted to")
        view = event.view_as(self.target_node)
        print("Full event text: ", view)
