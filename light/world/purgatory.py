#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import random
import threading
from typing import TYPE_CHECKING, List, Tuple, Type, Callable, Any, Optional, Dict

from light.world.souls.player_soul import PlayerSoul
from light.world.souls.tutorial_player_soul import TutorialPlayerSoul

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import GraphAgent
    from light.world.world import World
    from light.graph.events.base import GraphEvent
    from light.world.souls.soul import Soul

# Useful types
SoulArgProvider = Callable[[], List[Any]]
SoulProvider = Tuple[Type["Soul"], SoulArgProvider]


class Purgatory:
    """
    The Purgatory class is responsible for holding all of the Souls until the moment
    they are assigned a GraphAgent to inhabit. It is also the source from which Souls
    recieve observations, as the World is not aware of what Souls have inhabited
    the GraphAgents within.
    """

    def __init__(self, world: "World"):
        """
        Initializes the mappings of agent ids to souls, and additional state required
        to keep track of souls.
        """
        self.player_soul_id_to_soul = {}
        self.node_id_to_soul = {}
        self.filler_soul_providers: Dict[str, SoulProvider] = {}
        self.world = world
        self.player_assign_condition = threading.Condition()
        self.players = 0
        self.shared_args = {}

    def register_shared_args(self, arg_name, arg_provider):
        """
        Used to pass in e.g. the generic act model and roleplaying model scorer to souls.
        """
        if arg_provider is not None:
            self.shared_args[arg_name] = arg_provider

    def register_filler_soul_provider(
        self,
        provider_name: str,
        desired_soul_type: Type["Soul"],
        arg_provider: SoulArgProvider,
    ) -> None:
        """
        Register a source for Purgatory to be able to fill GraphAgents with souls. Purgatory
        will pick randomly from all of the registered soul providers, call the function for
        args, and then pass the target agent, world, and created args to the Soul.
        """
        self.filler_soul_providers[provider_name] = (desired_soul_type, arg_provider)

    def fill_soul(
        self, agent: "GraphAgent", wanted_provider: Optional[str] = None
    ) -> None:
        """
        Provide a filler soul for a graph agent. Select randomly from the filler soul
        providers to create the soul.
        """
        assert (
            self.node_id_to_soul.get(agent.node_id) is None
        ), "Cannot fill a soul that has someone already in it. call clear_soul first"
        if wanted_provider is not None:
            assert (
                wanted_provider in self.filler_soul_providers
            ), f"Requested provider {wanted_provider} is not registered"
        else:
            assert (
                len(self.filler_soul_providers) > 0
            ), "Must register at least one filler soul provider to fill souls"
            wanted_provider = random.choice(list(self.filler_soul_providers.keys()))
        soul_class, arg_provider = self.filler_soul_providers[wanted_provider]
        soul = soul_class(agent, self.world, *arg_provider())
        self.node_id_to_soul[agent.node_id] = soul

    def send_event_to_soul(self, event: "GraphEvent", agent: "GraphAgent"):
        """
        Pass an GraphEvent along to the soul inhabiting the given GraphAgent
        if such a soul exists, passing otherwise. Launch in wrapper around
        the async call such that the soul can choose to take its time
        deciding what to do.
        """
        if agent.get_prop("dead"):
            self.clear_soul(agent)
            return  # We shouldn't send an event to this soul, as it is reaped
        soul: "Soul" = self.node_id_to_soul.get(agent.node_id)
        if soul is not None:
            soul.wrap_observe_event(event)

    def clear_soul(self, agent: "GraphAgent") -> None:
        """Clear the soul that is associated with the given agent"""
        soul = self.node_id_to_soul.get(agent.node_id)
        if soul is not None:
            del self.node_id_to_soul[agent.node_id]
            soul.reap()

    def get_soul_for_player(
        self, player_provider, agent: Optional["GraphAgent"] = None
    ) -> Optional["Soul"]:
        """
        Create a player soul registered with the given player provider, returning
        the PlayerSoul if such a soul can be created, None if not (the world is full)
        """
        with self.player_assign_condition:
            possible_agents = self.world.get_possible_player_nodes()
            if len(possible_agents) > 0:
                target_agent = random.choice(possible_agents)
                self.clear_soul(target_agent)
                soul = PlayerSoul(
                    target_agent,
                    self.world,
                    self.players,
                    player_provider,
                    self.shared_args,
                )
                self.node_id_to_soul[target_agent.node_id] = soul
                self.player_soul_id_to_soul[self.players] = soul
                self.players += 1
                return soul
        return None


class TutorialPurgatory(Purgatory):
    """Version of purgatory that only ever puts a player into the tutorial character"""

    def get_soul_for_player(
        self,
        player_provider,
        agent: Optional["GraphAgent"] = None,
    ):
        with self.player_assign_condition:
            ag = list(self.world.oo_graph.agents.values())[0]
            assert ag.name == "You", f"Could not find you! {ag} instead"
            self.clear_soul(ag)
            soul = TutorialPlayerSoul(
                ag,
                self.world,
                self.players,
                player_provider,
                self.shared_args,
            )
            self.node_id_to_soul[ag.node_id] = soul
            self.player_soul_id_to_soul[self.players] = soul
            self.players += 1
            return soul
