#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import pandas as pd
import os
from typing import Dict, List, Optional
import json
from tqdm import tqdm


oldckpt2newckpt = {
    "/checkpoint/kshuster/projects/wizard_2.0/parlai_sweeps/bart_sweep1_Fri_Oct__2/395/model": "/checkpoint/light/projects/lightqa/wow/models/wow_baseline_bart/model",
    "/checkpoint/kshuster/projects/wizard_2.0/parlai_sweeps/take2_bart_sweep44_Sat_Mar_27/cb8/model": "/checkpoint/light/projects/lightqa/wow/models/wow_baseline_bart_rag_dpr/model",
    "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_knowledge_response_generation_sweep_4_Tue_Aug_31_1155/577/model": "/checkpoint/light/projects/lightqa/wow/models/wow_krm_bart_rag_dpr/model",
    "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_sweep_3_Wed_Aug_18_2130/ad6/model": "/checkpoint/light/projects/lightqa/wow/models/wow_drm_bart/model",
    "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_knowledge_sweep_1_Mon_Oct_11_1120/956/model": "/checkpoint/light/projects/lightqa/wow/models/wow_drm_conf_score_bart/model",
    "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_shared_model_sweep_1_Wed_Oct_06_1745/40f/model": "/checkpoint/light/projects/lightqa/wow/models/wow_krm_drm_shared_bart_rag_dpr/model",
    # '/checkpoint/kshuster/projects/wizard_2.0/parlai_sweeps/bart_sweep1_Fri_Oct__2/395/model':
    #     '/checkpoint/light/projects/lightqa/nq_open/models/nq_baseline_bart/model',
    # '/checkpoint/kshuster/projects/wizard_2.0/parlai_sweeps/take2_bart_sweep44_Sat_Mar_27/cb8/model':
    #     '/checkpoint/light/projects/lightqa/nq_open/models/nq_baseline_bart_rag_dpr/model',
    "/checkpoint/mpchen/projects/chatty_tasks/qa/t5fid/t9b_nq_singleValSweep_notCompressedMon_May_24/b09/model": "/checkpoint/light/projects/lightqa/nq_open/models/nq_krm_t5/model",
    # '/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_sweep_3_Wed_Aug_18_2130/ad6/model':
    #     '/checkpoint/light/projects/lightqa/nq_open/models/nq_drm_bart/model',
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_11_Thu_Sep_16_1320/a52/model": "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_baseline_bart_light/model",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_11_Thu_Sep_16_1320/2a8/model": "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_baseline_bart_summaryqa/model",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_11_Thu_Sep_16_1320/166/model": "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_baseline_bart_light_and_summaryqa/model",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_8_Thu_Sep_16_0953/974/model": "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_krm_bart_light/model",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_8_Thu_Sep_16_0953/3ed/model": "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_krm_bart_summaryqa/model",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_8_Thu_Sep_16_0953/375/model": "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_krm_bart_light_and_summaryqa/model",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_12_Thu_Sep_23_1335/27b/model": "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_krm_drm_shared_bart/model",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_10_Thu_Sep_16_1306/1d8/model": "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_drm_bart/model",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_9_Mon_Sep_13_1703/d13/model": "/checkpoint/light/projects/lightqa/lightqa/models/lightqa_drm_bart_confidence/model",
    "/checkpoint/ladolphs/projects/light/lightqa/wow/evals/final_evals/baseline_1_Mon_Oct_11_1902": "/checkpoint/light/projects/lightqa/wow/evals/wow_baseline",
    "/checkpoint/ladolphs/projects/light/lightqa/wow/evals/final_evals/s2s2s_1_Wed_Oct_13_1134": "/checkpoint/light/projects/lightqa/wow/evals/wow_k2r",
    "/checkpoint/ladolphs/projects/light/lightqa/nq_open/evals/final_evals/s2s2s_1_Mon_Oct_11_1346": "/checkpoint/light/projects/lightqa/nq_open/evals/nq_k2r",
    "/checkpoint/ladolphs/projects/light/lightqa/nq_open/evals/final_evals/baseline_1_Wed_Oct_13_1432": "/checkpoint/light/projects/lightqa/nq_open/evals/nq_baseline",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/evals/final_evals/baseline_1_Mon_Oct_11_1407": "/checkpoint/light/projects/lightqa/lightqa/evals/lightqa_baseline",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/evals/final_evals/s2s2s2_1_Mon_Oct_11_1407": "/checkpoint/light/projects/lightqa/lightqa/evals/lightqa_k2r",
}
newckpt2oldckpt = {v: k for k, v in oldckpt2newckpt.items()}

ckpt2model = {
    "/checkpoint/kshuster/projects/wizard_2.0/parlai_sweeps/bart_sweep1_Fri_Oct__2/395/model": "BART",
    "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_sweep_3_Wed_Aug_18_2130/ad6/model": "BART",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_11_Thu_Sep_16_1320/a52/model": "BART",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_11_Thu_Sep_16_1320/2a8/model": "BART",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_11_Thu_Sep_16_1320/166/model": "BART",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_8_Thu_Sep_16_0953/974/model": "BART",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_8_Thu_Sep_16_0953/3ed/model": "BART",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_8_Thu_Sep_16_0953/375/model": "BART",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_10_Thu_Sep_16_1306/1d8/model": "BART",
    "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_shared_model_sweep_1_Wed_Oct_06_1745/40f/model": "BART shared",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_12_Thu_Sep_23_1335/27b/model": "BART shared",
    "oracle": "Oracle",
    "/checkpoint/kshuster/projects/wizard_2.0/parlai_sweeps/take2_bart_sweep44_Sat_Mar_27/cb8/model": "BART RAG DPR",
    "/private/home/ladolphs/code/ParlAI/data/models/hallucination/bart_rag_token/model": "BART RAG DPR",
    "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_knowledge_response_generation_sweep_4_Tue_Aug_31_1155/577/model": "BART RAG DPR",
    "/checkpoint/mpchen/projects/chatty_tasks/qa/t5fid/t9b_nq_singleValSweep_notCompressedMon_May_24/b09/model": "T5",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_9_Mon_Sep_13_1703/d13/model": "BART conf-score",
    "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_knowledge_sweep_1_Mon_Oct_11_1120/956/model": "BART conf-score",
    "/checkpoint/kshuster/projects/wizard_internet/woi_sweep7_Wed_Jun__2/967/model": "BB2.7B",
    "/checkpoint/kshuster/projects/wizard_internet/woi_sweep4_Wed_Jun__2/cb2/model": "BB440M",
    "/checkpoint/kshuster/projects/wizard_internet/woi_sweep5_Wed_Jun__2/58b/model": "BART",
    "/checkpoint/kshuster/projects/wizard_internet/woi_sweep6_Wed_Jun__2/99a/model": "T5-Large",
    "/checkpoint/ladolphs/projects/light/lightqa/woi/sweeps/knowledge_response_sweep_1_Tue_Oct_19_1735/e22/model": "FiD Gold",
}

ckpt2traindata = {
    "/checkpoint/kshuster/projects/wizard_2.0/parlai_sweeps/bart_sweep1_Fri_Oct__2/395/model": "WoW",
    "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_sweep_3_Wed_Aug_18_2130/ad6/model": "WoW",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_11_Thu_Sep_16_1320/a52/model": "Light",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_11_Thu_Sep_16_1320/2a8/model": "LightQA",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_11_Thu_Sep_16_1320/166/model": "Light+LightQA",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_8_Thu_Sep_16_0953/974/model": "Light",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_8_Thu_Sep_16_0953/3ed/model": "LightQA",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/knowledge_response_sweep_8_Thu_Sep_16_0953/375/model": "Light+LightQA",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_10_Thu_Sep_16_1306/1d8/model": "Light",
    "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_shared_model_sweep_1_Wed_Oct_06_1745/40f/model": "WoW",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_12_Thu_Sep_23_1335/27b/model": "Light",
    "oracle": "-",
    "/checkpoint/kshuster/projects/wizard_2.0/parlai_sweeps/take2_bart_sweep44_Sat_Mar_27/cb8/model": "WoW",
    "/private/home/ladolphs/code/ParlAI/data/models/hallucination/bart_rag_token/model": "WoW",
    "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_knowledge_response_generation_sweep_4_Tue_Aug_31_1155/577/model": "WoW",
    "/checkpoint/mpchen/projects/chatty_tasks/qa/t5fid/t9b_nq_singleValSweep_notCompressedMon_May_24/b09/model": "NQ",
    "/checkpoint/ladolphs/projects/light/lightqa/lightqa/sweeps/dialogue_response_sweep_9_Mon_Sep_13_1703/d13/model": "Light",
    "/checkpoint/ladolphs/projects/light/lightqa/wow/sweeps/wow_dialogue_response_knowledge_sweep_1_Mon_Oct_11_1120/956/model": "WoW",
}


def get_train_data_from_ckpt(ckpt: str) -> str:
    if ckpt in newckpt2oldckpt:
        # Convert to old ckpt
        ckpt = newckpt2oldckpt[ckpt]
    if ckpt in ckpt2traindata:
        return ckpt2traindata[ckpt]
    # No train data found
    return "NA"


def get_model_from_ckpt(ckpt: str) -> str:
    if ckpt in newckpt2oldckpt:
        # Convert to old ckpt
        ckpt = newckpt2oldckpt[ckpt]
    if ckpt in ckpt2model:
        return ckpt2model[ckpt]
    # No model found
    return ckpt


def load_all_exps(eval_paths: Dict):
    dfs = {}
    for k, path in tqdm(eval_paths.items()):
        eval_dirs = get_eval_directories(path)
        new_df = df_from_eval_runs(eval_dirs)
        new_df["exp_id"] = k
        dfs[k] = new_df

    df = pd.concat(list(dfs.values()))
    return dfs, df


def get_eval_directories(directory: str):
    """
    Return the subdirectories for eval.
    """
    exclude_dirs = ["ParlAI", "slurm_logs"]
    return [
        os.path.join(directory, name)
        for name in filter(
            lambda name: os.path.isdir(os.path.join(directory, name))
            and name not in exclude_dirs,
            os.listdir(directory),
        )
    ]


def read(fname):
    with open(fname, "r") as f:
        if fname.endswith(".json"):
            data = json.load(f)
        else:
            data = f.readlines()
    return data


def parse_run_info(run_cmd: str) -> Dict:
    cmd = run_cmd.split()
    res = {}

    for i in range(len(cmd)):
        if cmd[i].startswith("-") and i + 1 < len(cmd):
            k, v = cmd[i].strip("-"), cmd[i + 1]
            if ", " in v and ":" in v:
                for sub_option in v.split(","):
                    sub_k, sub_v = sub_option.split(":")
                    res[f"{k}__{sub_k}"] = sub_v
            else:
                res[k] = v
    return res


def df_from_eval_runs(eval_dirs: List[str], verbose=False):
    rows = []
    for eval_dir in eval_dirs:

        # Get the run cmd.
        run_file = os.path.join(eval_dir, "run.sh")
        run_cmd = [l for l in read(run_file) if l.startswith("python")][0]
        run_opts = parse_run_info(run_cmd)

        # Get the final metrics.
        if "eval_stats.json" in os.listdir(eval_dir):
            eval_file = os.path.join(eval_dir, "eval_stats.json")
            eval_dict = read(eval_file)
            complete_percentage = 100.0
            results = eval_dict["report"]
            if verbose:
                print(f'Evaluation completed for "{eval_dir.split("/")[-1]}".')

        elif any("stdout" in fname for fname in os.listdir(eval_dir)):
            stdout_file = os.path.join(
                eval_dir, [f for f in os.listdir(eval_dir) if f.startswith("stdout")][0]
            )
            stdout = read(stdout_file)

            # Find the status line with the highest complete percentage.
            highest_status_line_idx, complete_percentage = None, 0
            for i, line in enumerate(stdout):
                # Find the best status update line.
                if all(kword in line for kword in ["complete", "elapsed", "eta"]):
                    new_complete_percentage = float(line.split("|")[1].split("%")[0])
                    if new_complete_percentage > complete_percentage:
                        highest_status_line_idx, complete_percentage = (
                            i,
                            new_complete_percentage,
                        )

            if highest_status_line_idx is None:
                if verbose:
                    print(f'No results yet to report for "{eval_dir.split("/")[-1]}".')
                continue
            if verbose:
                print(stdout[highest_status_line_idx])

            # Parse all the information.
            status_line = stdout[highest_status_line_idx]
            complete_percentage = float(status_line.split("|")[1].split("%")[0])
            key_lines = []
            for i in range(highest_status_line_idx + 1, len(stdout), 2):
                key_line = stdout[i]
                key_lines.append(key_line)
                if not key_line.strip().endswith("\\"):
                    break
            value_lines = stdout[highest_status_line_idx + 2 :: 2][: len(key_lines)]

            keys = [
                k
                for k in " ".join(
                    l.strip().replace("\\", " ") for l in key_lines
                ).split(" ")
                if k
            ]
            values = [
                float(v.strip())
                for v in " ".join(
                    l.strip().replace("\\", " ") for l in value_lines
                ).split(" ")
                if v
            ]
            results = dict(zip(keys, values))

        else:
            if verbose:
                print(f'No results available for "{eval_dir.split("/")[-1]}".')
            continue

        results = {
            **results,
            **dict(
                complete_percentage=complete_percentage,
                run_cmd=run_cmd,
                eval_dir=eval_dir,
            ),
            **run_opts,
        }

        rows.append(results)

    return pd.DataFrame.from_dict(rows)


def save_to_csv(df, filename, save_dir=None, eval_dir=None):
    if not filename.endswith(".csv"):
        filename += ".csv"
    if save_dir is None:
        save_dir = "/private/home/ladolphs/code/ParlAI/parlai_internal/projects/light/lightqa/data/notebooks/dfs"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    save_path = os.path.join(save_dir, filename)
    df.to_csv(save_path)
    print(f'Saved df to "{save_path}"')

    if eval_dir:
        save_path = os.path.join(eval_dir, filename)
        df.to_csv(save_path)
        print(f'Saved df to "{save_path}"')


def get_view(
    df,
    non_standard_cols: Optional[List[str]] = None,
    removed_cols: Optional[List[str]] = None,
    sort_key: str = "f1",
    ascending: bool = False,
    conditions: Optional[Dict] = None,
):
    df_view = df
    cols_orig = [
        "exp_id",
        "complete_percentage",
        "response-model",
        "knowledge-model",
        "rm-train-data",
        "km-train-data",
        "n-docs",
        "knowledge-response-model-options__beam_min_length",
        "dialogue-response-model-options__beam_min_length",
        "ppl",
        "f1",
        "knowledge_f1",
        "knowledge_f1_sentences",
        "knowledge_f1_max_sentences",
        "rare_word_f1",
        "predicted_knowledge_f1",
        "bleu-4",
        "rouge_L",
        "krm-indexer-type",
        "indexer-type",
        "beam-min-length",
        "beam-size",
        "add-fixed-confidence",
        "krm-beam-min-length",
        "drm-beam-min-length",
        "drm-beam-size",
        "krm-beam-size",
        "beam-filter-for-knowledge-response",
        "add-confidence-as-str",
        "accuracy",
        "krm_em",
        "kaa",
        "pkaa",
        "ka_rec",
        "krm_norm_em",
        "krm_norm_f1",
        "pka_rec",
        "krm-fp16",
        "drm-fp16",
        "mf",
        "model-file",
        "t",
        "dt",
        "datatype",
        "krm-n-docs",
        "mutators",
        "multitask_weights",
        "dialogue-response-model-path",
        "knowledge-response-model-path",
    ]

    if non_standard_cols:
        cols_orig += non_standard_cols
    if removed_cols:
        cols_orig = [c for c in cols_orig if c not in removed_cols]

    cols = list(filter(lambda c: c in df_view.columns, cols_orig))
    if "t" in cols:

        def apply_mapping(name):
            mapping = {
                "parlai_internal.projects.light.lightqa.wow.task.agents:WizardOfWikipediaGeneratorTeacher:random_split": "WoW seen",
                "parlai_internal.projects.light.lightqa.wow.task.agents:WizardOfWikipediaGeneratorTeacher:topic_split": "WoW unseen",
            }
            if name in mapping:
                return mapping[name]
            return name.split(":")[-1]

        df_view.loc[:, "t"] = df_view["t"].apply(apply_mapping)

    if "mf" in cols or "model-file" in cols:
        k = "mf" if "mf" in cols else "model-file"
        # df_view['response-model'] = df_view[k].apply(lambda name: ckpt2model.get(name, name))
        # df_view['rm-train-data'] = df_view[k].apply(lambda name: ckpt2traindata.get(name, name))
        df_view["response-model"] = df_view[k].apply(get_model_from_ckpt)
        df_view["rm-train-data"] = df_view[k].apply(get_train_data_from_ckpt)

    if "dialogue-response-model-path" in cols:
        k = "dialogue-response-model-path"
        df_view["response-model"] = df_view[k].apply(get_model_from_ckpt)
        df_view["rm-train-data"] = df_view[k].apply(get_train_data_from_ckpt)

    if "knowledge-response-model-path" in cols:
        k = "knowledge-response-model-path"
        df_view["knowledge-model"] = df_view[k].apply(get_model_from_ckpt)
        df_view["km-train-data"] = df_view[k].apply(get_train_data_from_ckpt)

    if "complete_percentage" in cols:
        complete_scores = df_view.complete_percentage.unique()
        if len(complete_scores) == 1 and complete_scores[0] == 100.0:
            df_view.drop(columns=["complete_percentage"], inplace=True)

    cols = list(filter(lambda c: c in df_view.columns, cols_orig))
    df_view = df_view[cols]

    if conditions:
        for k, v in conditions.items():
            if k in df_view.columns:
                df_view = df_view[df_view[k] == v]

    if sort_key in df_view.columns:
        df_view = df_view.sort_values(by=[sort_key], ascending=ascending)
    return df_view
