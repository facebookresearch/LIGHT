#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List, Type
from light.graph.events.base import (
    GraphEvent,
)

from light.graph.events.use_events import UseEvent
from light.graph.events.graph_events import (
    SayEvent,
    ShoutEvent,
    WhisperEvent,
    TellEvent,
    GoEvent,
    UnfollowEvent,
    FollowEvent,
    UnblockEvent,
    BlockEvent,
    HelpEvent,
    HitEvent,
    HugEvent,
    GetObjectEvent,
    PutObjectInEvent,
    DropObjectEvent,
    StealObjectEvent,
    GiveObjectEvent,
    EquipObjectEvent,
    WearEvent,
    WieldEvent,
    RemoveObjectEvent,
    IngestEvent,
    EatEvent,
    DrinkEvent,
    SoulSpawnEvent,
    ExamineEvent,
    EmoteEvent,
    WaitEvent,
    InventoryEvent,
    QuestEvent,
    HealthEvent,
    LookEvent,
    RewardEvent,
    PointEvent,
)

ALL_EVENTS_LIST: List[Type[GraphEvent]] = [
    SayEvent,
    ShoutEvent,
    WhisperEvent,
    TellEvent,
    GoEvent,
    UnfollowEvent,
    FollowEvent,
    UnblockEvent,
    BlockEvent,
    HelpEvent,
    HitEvent,
    HugEvent,
    GetObjectEvent,
    PutObjectInEvent,
    DropObjectEvent,
    StealObjectEvent,
    GiveObjectEvent,
    EquipObjectEvent,
    WearEvent,
    WieldEvent,
    RemoveObjectEvent,
    IngestEvent,
    EatEvent,
    DrinkEvent,
    SoulSpawnEvent,
    # LockEvent,
    # UnlockEvent,
    ExamineEvent,
    EmoteEvent,
    WaitEvent,
    InventoryEvent,
    QuestEvent,
    HealthEvent,
    LookEvent,
    UseEvent,
    RewardEvent,
    PointEvent,
]

ALL_EVENTS = {name: e for e in ALL_EVENTS_LIST for name in e.NAMES}
