#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Simple binary operators to store info for users into ints,
at least while we're still using the sqlite db for all this
"""

# Flags for having seen specific tutorial tips
FLAG_COMPLETED_ONBOARDING = 0
FLAG_HAS_ACTED = 1
FLAG_HAS_TOLD = 2
FLAG_GOT_EXP = 3
FLAG_CAN_GIFT = 4
FLAG_GOTTEN_GOALS = 5


def test_bit(int_type, offset):
    """Returns true if the bit at 'offset' is one"""
    mask = 1 << offset
    return not ((int_type & mask) == 0)


def set_bit(int_type, offset):
    """Returns an integer with the bit at offset set to 1"""
    mask = 1 << offset
    return int_type | mask


def clear_bit(int_type, offset):
    """Returns an integer with the bit at offset cleared"""
    mask = ~(1 << offset)
    return int_type & mask


def toggle_bit(int_type, offset):
    """Returns an integer with the bit at offset flipped"""
    mask = 1 << offset
    return int_type ^ mask


class OnboardingFlags:
    def __init__(self, flag: int):
        self.__flag = flag
        self.completed_onboarding = test_bit(flag, FLAG_COMPLETED_ONBOARDING)
        self.has_acted = test_bit(flag, FLAG_HAS_ACTED)
        self.has_told = test_bit(flag, FLAG_HAS_TOLD)
        self.got_exp = test_bit(flag, FLAG_GOT_EXP)
        self.gotten_goals = test_bit(flag, FLAG_GOTTEN_GOALS)

    def flag_did_update(self):
        return self.get_flag() != self.__flag

    def get_flag(self):
        flag = 0
        if self.completed_onboarding:
            flag = set_bit(flag, FLAG_COMPLETED_ONBOARDING)
        if self.has_acted:
            flag = set_bit(flag, FLAG_HAS_ACTED)
        if self.has_told:
            flag = set_bit(flag, FLAG_HAS_TOLD)
        if self.got_exp:
            flag = set_bit(flag, FLAG_GOT_EXP)
        if self.gotten_goals:
            flag = set_bit(flag, FLAG_GOTTEN_GOALS)
        return flag
