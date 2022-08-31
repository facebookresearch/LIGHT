#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
f = open("room_labels.txt", "r")
fw = open("room_labels_final.txt", "w")

s = f.read().split("\n")

labels = {"y", "n", "m", "g", "b", "c", "r"}
numbers = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}

counts = {}
tot = 0

for r in s:
    if r != "":
        c = r[0]
        if c == "r":
            c = "y"
        if r[1] in numbers:
            if c not in labels:
                import pdb

                pdb.set_trace()
            id = r[1:-1].split(" ")[0]
            if c not in counts:
                counts[c] = 0
            counts[c] += 1
            tot += 1
            fw.write(id + " " + c + "\n")
    # s = str(r ) + " " + x['category'] + " " + x['setting'] + " " + x['background'] + '\n'
fw.close()


for c, v in counts.items():
    # print(c,v)
    print(c + " " + str(v) + "  (" + str(float(v) / tot) + "%)")

print("total:", tot)

# import pdb; pdb.set_trace()
