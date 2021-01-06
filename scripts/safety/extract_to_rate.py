import os

OUT_DIR = os.path.expanduser("~/LIGHT/scripts/safety/out/")

def parse_safety_line(in_line, safe_threshold=0.850):
    parsed = in_line.split(',')
    
    rating = parsed[1].strip() == 'True'
    confidence = float(parsed[2].strip())
    text = ",".join(parsed[3:])
    return text.strip(), rating is True or confidence < safe_threshold

def parse_is_light_line(in_line, is_light_threshold=0.70):
    parsed = in_line.split(',')
    
    rating = parsed[1].strip() == 'True'
    confidence = float(parsed[2].strip())
    text = ",".join(parsed[3:])
    return text.strip(), rating is False or confidence < is_light_threshold


LIGHT_FILES = ['turn_lightings.txt', 'wild_turn_lightings.txt']
SAFETY_FILES = ['turn_ratings.txt', 'wild_turn_ratings.txt']

all_lines = []

for fn in LIGHT_FILES:
    with open(os.path.join(OUT_DIR, fn), 'r') as light_file:
        lines = light_file.readlines()
        all_lines += [parse_is_light_line(l) for l in lines]

for fn in SAFETY_FILES:
    with open(os.path.join(OUT_DIR, fn), 'r') as safety_file:
        lines = safety_file.readlines()
        all_lines += [parse_safety_line(l) for l in lines]

important_lines = set([l for (l, keep) in all_lines if keep])

TURN_TO_EVAL_FILE = 'turns_to_eval.txt'

with open(os.path.join(OUT_DIR, TURN_TO_EVAL_FILE), 'w+') as light_file:
    for line in important_lines:
        light_file.write(line + '\n')
