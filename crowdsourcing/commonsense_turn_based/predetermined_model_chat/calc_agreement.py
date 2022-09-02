import pandas as pd
import pingouin as pg
from collections import Counter
df = pd.read_csv("rating_df.csv")

r_keys = ['inconsistent_setting', 'inconsistent_action', 'disfluent', 'none_all_good']
for r in r_keys:
    df[r] = df[r].astype(int)

# print(df[[c for c in df.columns if "input" not in c]])
# print(df.dropna())

workers = df['worker']
print(Counter(workers))

# good_workers = [w for w in workers if Counter(workers)[w] >= 5]
good_workers = [w for w in workers]

inputs = list(set(df['input']))
df['input_ids'] = [inputs.index(i) for i in df['input']]

for key in r_keys:
    print(f"Current key: {key}")
    better_rows = []
    for i, row in df.iterrows():
        if row['worker'] in good_workers:
            # better_rows.append([row['input'], row['worker'], row[key]])
            better_rows.append([row['input_ids'], row['worker'], row[key]])
    all_ids = [row[0] for row in better_rows]
    good_inputs = [row[0] for row in better_rows if all_ids.count(row[0]) == 3]
    # input_to_ratings = {}
    best_rows = []
    for this_input in good_inputs:
        relevant_rows = [r for r in better_rows if r[0] == this_input]
        worker_names = ["a", "b", "c"]
        for i, r in enumerate(relevant_rows):
            best_rows.append([this_input, worker_names[i], r[2]])

    # best_rows = []
    # for row in better_rows:
    #     if row[0] in good_inputs:
    #         best_rows.append(row)
    # this_df = pd.DataFrame(better_rows, columns=["input", "worker", key])
    this_df = pd.DataFrame(best_rows, columns=["input", "worker", key])
    # print(this_df)
    # print(this_df)
    data = this_df.pivot_table(index="input", columns="worker", values=key, observed=True)
    print(data)
    # nan_present = data.isna().any().any()
    # print(nan_present)

    # Listwise deletion of missing values
    nan_present = data.isna().any().any()

    icc = pg.intraclass_corr(data=this_df, targets='input', raters='worker', ratings=key, nan_policy='omit')
    # icc = pg.intraclass_corr(data=this_df, targets='input', raters='worker', ratings=key)

    icc.set_index('Type')
    print(icc)
    # break