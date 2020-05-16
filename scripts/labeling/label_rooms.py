#!/usr/bin/env python3
import pickle
print("hi")

file = open("light_jfixed_environment.pkl",'br')
d = pickle.load(file)

fw = open('room_labels.txt','w')

for r in d['rooms'].keys():
    x = d['rooms'][r]
    s = str(r ) + " " + x['category'] + " " + x['setting'] + " " + x['background'] + '\n'
    fw.write(s + '\n')

fw.close()
    
#import pdb; pdb.set_trace()
