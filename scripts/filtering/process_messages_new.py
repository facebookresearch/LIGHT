import os
import json
import math
from datetime import datetime, timedelta

ROOT_PATH = "/checkpoint/light/data/wild_chats/"
# ROOT_PATH = os.path.expanduser("~/Desktop/Hobbot_chats/")

TARGET_FILES = [
    # Wave 1
    os.path.join(ROOT_PATH, "light_chats_00-00-00_to_05-26-20.json"),
    os.path.join(ROOT_PATH, "light_chats_05-27-20_to_06-23-20.json"),
    # Wave 2
    os.path.join(ROOT_PATH, "light_chats_06-24-20_to_06-28-20.json"),
    os.path.join(ROOT_PATH, "light_chats_06-29-20_to_06-30-20.json"),
    os.path.join(ROOT_PATH, "light_chats_07-01-20_to_07-05-20.json"),
    # Wave 3
    os.path.join(ROOT_PATH, "light_chats_07-06-20_to_07-08-20.json"),
    os.path.join(ROOT_PATH, "light_chats_07-09-20.json"),
    os.path.join(ROOT_PATH, "light_chats_07-10-20.json"),
    os.path.join(ROOT_PATH, "light_chats_07-11-20.json"),
    os.path.join(ROOT_PATH, "light_chats_07-12-20.json"),
    os.path.join(ROOT_PATH, "light_chats_07-13-20_to_07-16-20.json"),
]

chats = []
for TARGET_FILE in TARGET_FILES:
    with open(TARGET_FILE, "r") as chat_file:
        chats += json.load(chat_file)

if isinstance(chats, dict):
    headers = chats["header"]
    rows = chats["rows"]
    chats = []
    for row in rows:
        chat = {}
        for idx, header in enumerate(headers):
            chat[headers[idx]] = row[idx]
        chats.append(chat)


def remove_cand_path(in_path):
    fcp_split = in_path.split("fixed_candidates_path")
    pre_fixed_cands = fcp_split[0]
    post_fixed_cands = fcp_split[1].split("/")[-1]
    check = pre_fixed_cands + "fixed_candidates_path=" + post_fixed_cands
    return check.replace("==", "=").replace("encode_candidate_vecs=True,", "")


for c in chats:
    c["model_name"] = remove_cand_path(c["model_name"])
    for key in ["dialogue", "human_persona", "bot_persona"]:
        try:
            c[key] = json.loads(c[key].replace('\\\\"', '\\"'))
        except:
            try:
                c[key] = json.loads(c[key])
            except:
                print(key, c[key], type(c[key]))
                raise

chats = [c for c in chats if c["dialogue"] is not None and len(c["dialogue"]) > 1]

for c in chats:
    last_chat = c["dialogue"][-1]
    if last_chat["type"] == "choice":
        c["choice"] = last_chat
        c["dialogue"] = c["dialogue"][:-1]
    else:
        c["choice"] = None

    c["location"] = c["dialogue"][0]
    c["dialogue"] = c["dialogue"][1:]


def get_flagged(in_chats):
    return [c for c in in_chats if c["flagged_messages"] is not None]


def split_chats(
    in_chats, from_datetime=None, to_datetime=None, from_time_str=None, to_time_str=None
):
    if to_time_str is None:
        if to_datetime is None:
            to_time = datetime.now()
        else:
            to_time = to_datetime
    else:
        to_time = datetime.strptime(to_time_str, "%Y-%m-%d-%H-%M-%S")

    if from_time_str is None:
        if from_datetime is None:
            from_time = datetime.fromtimestamp(0)
        else:
            from_time = from_datetime
    else:
        from_time = datetime.strptime(from_time_str, "%Y-%m-%d-%H-%M-%S")

    filtered_chats = []
    for c in chats:
        c_time = datetime.strptime(c["ts"], "%Y-%m-%d-%H-%M-%S")
        if c_time < from_time:
            continue
        if c_time > to_time:
            continue
        filtered_chats.append(c)
    return filtered_chats


def choice_stats(in_chats):
    fin_go = 0
    fin_new_partner = 0
    fin_new_persona = 0
    fin_exit = 0
    missing = 0
    for chat in in_chats:
        choice = chat["choice"]
        if choice is None:
            missing += 1
        elif choice["text"].startswith("Go"):
            fin_go += 1
        elif choice["text"].startswith("New Partner"):
            fin_new_partner += 1
        elif choice["text"].startswith("New Persona"):
            fin_new_persona += 1
        else:
            fin_exit += 1
    continue_rate = 1 - (fin_exit + missing) / len(in_chats)
    print(
        f"Continue Rate: {continue_rate}, Go: {fin_go}, Partner: {fin_new_partner}, Persona: {fin_new_persona}, Exit: {fin_exit}, missing: {missing}"
    )


def chat_stats(in_chats):
    fin_stats = []
    total_utts = 0
    total_words = 0
    total_chats = len(in_chats)
    for chat in in_chats:
        messages = chat["dialogue"]
        human_messages = [m["text"] for m in messages if m["id"] == "human"]
        utt_count = len(human_messages)
        if utt_count == 0:
            print(messages)
        words = " ".join(human_messages).split(" ")
        avg_utt_len = len(words) / utt_count
        total_utts += utt_count
        total_words += len(words)
        fin_stats.append(
            {
                "words": len(words),
                "utts": utt_count,
                "avg_len": avg_utt_len,
                "messages": messages,
            }
        )
    print(
        f"Total Chats: {total_chats}, Total utts: {total_utts}, Total Words: {total_words}, avg chat len {total_utts/total_chats}, avg utt len {total_words/total_utts}"
    )
    return fin_stats


def get_quests(in_chats):
    return [c for c in in_chats if "motivation" in c["human_persona"]]


def split_chats_by_model(chats):
    model_chats = {}
    for c in chats:
        model = c["model_name"]
        if model not in model_chats:
            model_chats[model] = []
        model_chats[model].append(c)
    return model_chats


def has_action(quest):
    return len([a for a in quest["dialogue"] if a["type"] == "action"]) > 0


def get_actioned_quests(quests):
    return [q for q in quests if has_action(q)]


def quest_successful(quest):
    actions = [a for a in quest["dialogue"] if a["type"] == "action"]
    return len([a for a in actions if a["score"]]) > 0


def quest_hit_goal(quest):
    actions = [a for a in quest["dialogue"] if a["type"] == "action"]
    return len([a for a in actions if a["text"] == quest["human_persona"]["goal"]]) > 0


def get_continue_rate_stats_for_chats(in_chats):
    continues = len(
        [
            c
            for c in in_chats
            if c["choice"] is not None and c["choice"]["text"] != "EXIT"
        ]
    )
    total = len(in_chats)
    exits = total - continues
    estimate_p = continues / total
    Z = 1.9599
    error = Z / (2 * math.sqrt(total))
    return estimate_p, error


def estimate_model_continue_rates(chats_by_model):
    model_keys_sorted = sorted(list(chats_by_model.keys()))
    print(f"Calculating continue rate and error at 95% confidence")
    for model_key in model_keys_sorted:
        model_chats = chats_by_model[model_key]
        prob, error = get_continue_rate_stats_for_chats(model_chats)
        print(f"Model: {model_key}")
        print(f"Continue rate: {prob:0.3f} +/- {error:0.3f}, count: {len(model_chats)}")


quest_chats = get_quests(chats)
perfect_quests = [q for q in quest_chats if quest_hit_goal(q)]
doable_quests = [q for q in quest_chats if quest_successful(q)]

import code

code.interact(local=locals())
