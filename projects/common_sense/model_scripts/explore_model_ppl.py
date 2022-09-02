from enum import unique
import json
import pandas as pd
import os


eval_report_prefix = "/checkpoint/light/common_sense/model_data/bart_compare_largersweep_Sun_Aug_14/eval_reports"
model_opt_prefix = "/checkpoint/light/common_sense/model_data/bart_compare_largersweep_Sun_Aug_14"

# names = [f for f in os.listdir(eval_report_prefix) if "test" in f]
names = ['test_341.json', 'test_c8f.json']

hyper_params = ['graph_input_do', 'game_text_do', 'learningrate']

name_to_data = {}
row_data = []

# just for comparing hyper-parameters
unique_setups_to_results = {}

for name in names:
    # nice_name is the model name (e.g. c4e)
    nice_name = name.replace("test_", "").replace("train_", "").replace(".json", "")
    row = [nice_name]

    # get eval report
    with open(f"{eval_report_prefix}/{name}", "r") as f:
        d = f.read()

    data = json.loads(d)

    # also load model.opt to get some of the sweep parameters the model was trained with
    with open(f"{model_opt_prefix}/{nice_name}/model.opt", "r") as f:
        d = f.read()

    model_opt = json.loads(d)

    report = data['report']

    # get each task the report contains
    tasks = set()
    for key in report.keys():
        if "internal:" in key:
            tasks.add(key.split("/")[0])
    # to ensure consistency
    tasks = sorted(tasks)
    
    # get the perplexity of each of these tasks, rounded to 3 decimal places
    ppls = []
    for t in tasks:
        ppl = round(float(report[f"{t}/ppl"]), 3)
        row.append(ppl)
        ppls.append(ppl)
    
    # save each of the relevant hyper-parameters
    h_values = []
    for h in hyper_params:
        h_value = model_opt[h]
        row.append(h_value)
        h_values.append(h_value)
    h_values = tuple(h_values)
    
    # row.append(data["MANUAL_GROUNDED"])
    is_grounded = "internal:light_common_sense:AddCharacterWieldingTeacher" in model_opt["task"]
    row.append(is_grounded)
    row_data.append(row)

    if h_values not in unique_setups_to_results:
        unique_setups_to_results[h_values] = []
    unique_setups_to_results[h_values].append([*ppls, sum(ppls) / len(ppls), is_grounded])
    
nice_tasks = [t.split(":")[-1].replace("NarrationTeacher", "") for t in tasks]

df = pd.DataFrame(data=row_data, columns=["Name", *nice_tasks, *hyper_params, "grounded"])

# get mean ppl across these tasks
df['mean_ppl'] = df[nice_tasks].mean(axis=1).round(3)

# df = df.sort_values(by=["GameActionsNarrationTeacher"])
# df = df.sort_values(by=["GameActions"])
# df = df.sort_values(by=["InvalidSelfPlay"])
df = df.sort_values(by=["mean_ppl"])

print(df)

# Print to make it easier to copy into other tables
# print()
# print("\t".join(df.columns))
# for i, row in df.iterrows():
#     vals = [str(row[c]) for c in df.columns]
#     print("\t".join(vals))


# Compare directly the same hyper-parameter setups

setups = df[["graph_input_do", "game_text_do", "learningrate"]]

unique_setups = setups.drop_duplicates()
# print(unique_setups)

grounded_better = 0
nongrounded_better = 0
for setup, results in unique_setups_to_results.items():
    grid, gatd, lr = setup
    grounded_mean = -1
    nongrounded_mean = -1
    for res in results:
        if res[-1]:
            # grounded_mean = res[-2]
            grounded_mean = res[3]
        else:
            nongrounded_mean = res[3]
    if grounded_mean < nongrounded_mean:
        # print(f"GROUNDED BETTER: {round(grounded_mean, 3)} < {round(nongrounded_mean, 3)}")
        grounded_better += 1
    else:
        # print(f"NONGROUNDED BETTER: {round(grounded_mean, 3)} > {round(nongrounded_mean, 3)}")
        nongrounded_better += 1

print(f"Comparing setups (grounded vs ungrounded with same hyper-params)")
print(f"In total: {grounded_better} grounded vs {nongrounded_better} nongrounded")