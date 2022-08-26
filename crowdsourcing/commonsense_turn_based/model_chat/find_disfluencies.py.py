import jsonlines
import copy

# fname = "/checkpoint/alexgurung/light/common_sense/compare_grounding/world_logs/341/341_internal:light_common_sense:InvalidSelfPlayNarrationTeacher.jsonl"
fname = "/checkpoint/alexgurung/light/common_sense/compare_grounding/world_logs/6ce/6ce_internal:light_common_sense:InvalidSelfPlayNarrationTeacher.jsonl"
dialogs = []
with jsonlines.open(fname, "r") as f:
    for line in f:
        dialogs.append(line)

task_data = []
for item in dialogs:
    this_dialog = item['dialog']
    this_dialog = this_dialog[0]
    teacher_dialog = this_dialog[0]
    game_text = teacher_dialog['game_text_dropoutless']
    teacher_dialog["response_text"] = this_dialog[1]['text']
    # this_game_texts.add(game_text)
    task_data.append(teacher_dialog)

new_task_data = []
for t in task_data:
    if len(t['setting_context_text_dropoutless']) == 0:
        continue    
    new_task_data.append(copy.deepcopy(t))
    new_task_data[-1]['saved_contextual_data'] = copy.deepcopy(t)
task_data = new_task_data

for t in task_data:
    # print(t.keys())
    resp = t['response_text']
    true = t['eval_labels']
    words = resp.split(" ")
    found = False
    for w in words:
        if "'" in w and w not in ("don't", "can't", "isn't", "won't", "You're", "aren't"):
            if not w.startswith("'") and not w.endswith("'") and "'s" not in w:
                found = True
    if found:
        print("-"*100)
        print(resp)
        print(true)