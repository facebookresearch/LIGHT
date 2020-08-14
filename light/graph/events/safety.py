#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai.utils.safety import OffensiveStringMatcher


class SafetyClassifier:
    def __init__(self, datapath):
        if datapath != "":
            self.classifier = OffensiveStringMatcher(datapath)
        else:
            self.classifier = None
            
    def is_safe(self, text):
        if self.classifier is None:
            return True
        else:
            text = text.lstrip('"')
            text = text.rstrip('"')
            return not (text in self.classifier)
