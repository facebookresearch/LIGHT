# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3
import pickle

print("hi")

file = open("light_jfixed_environment.pkl", "br")
d = pickle.load(file)

fw = open("room_labels.txt", "w")

for r in d["rooms"].keys():
    x = d["rooms"][r]
    s = str(r) + " " + x["category"] + " " + x["setting"] + " " + x["background"] + "\n"
    fw.write(s + "\n")

fw.close()

# import pdb; pdb.set_trace()
