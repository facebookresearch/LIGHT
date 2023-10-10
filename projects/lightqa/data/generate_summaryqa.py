#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Generate SummaryQA data based on light-dialog-wild.

We summarize light data using a summarization model. Based on the summary, we
extract possible "answers" as noun chunks in the summary. Using the summary as
context and the answers, we generate a question.

The dialogues are modified such that they always end with the partner asking
a question. The label is the answer, not a dialogue response.
"""

import os
from tqdm import tqdm
from typing import List, Tuple

from parlai.core.params import ParlaiParser
from parlai.core.script import ParlaiScript
from parlai.core.worlds import _create_task_agents

from parlai_internal.projects.light.lightqa.data.question_generator import (
    QuestionGenerator,
    SummarizationModel,
)
from parlai_internal.projects.light.lightqa.data.utils import save_json


def setup_args(parser=None):
    if parser is None:
        parser = ParlaiParser(True, True, "")
    parser.add_argument(
        "--save-path",
        type=str,
        default="",
        help="Save the responses as json file.",
    )
    parser.add_argument(
        "--verbose",
        type=bool,
        default=False,
        help="Print the examples.",
    )
    parser.add_argument(
        "--device",
        type=int,
        default=0,
        help="Device to use for the models.",
    )
    parser.add_argument(
        "--start-episode-idx",
        type=int,
        default=0,
        help="Start episode index.",
    )
    parser.add_argument(
        "--end-episode-idx",
        type=int,
        default=-1,
        help="End episode index.",
    )
    parser.set_defaults(
        task="light_dialog_wild",
    )
    return parser


def extract_persona_names(lines: List[str]) -> Tuple[str, str]:
    def extract_name(name_token):
        # Extract the names.
        name_line = [l for l in lines if l.startswith(name_token)]
        if not name_line:
            return ""
        name = name_line[0].replace(name_token, "").strip()
        return name

    self_name = extract_name("_self_name")
    partner_name = extract_name("_partner_name")
    return self_name, partner_name


def generate_history(lines: List[str]) -> str:
    self_name, partner_name = extract_persona_names(lines)

    if not self_name or not partner_name:
        return ""

    lines_to_remove = [
        "_task_speech",
        "_partner_name",
        "_self_name",
    ]

    kwords_to_replace = {
        "_setting_name": "",
        "_setting_desc": "",
        "_self_persona": self_name,
        "_self_say": self_name,
        "_partner_say": partner_name,
    }

    lines_to_put_in_quotes = [
        "_self_persona",
        "_self_say",
        "_partner_say",
    ]

    modified_lines = []
    for idx, line in enumerate(lines):
        if any([line.startswith(blocked_line) for blocked_line in lines_to_remove]):
            continue

        if not line or not line.split():
            continue
        kword = line.split()[0]
        replaced_kword = kwords_to_replace.get(kword, kword)
        text = " ".join(line.split()[1:])
        if any([line.startswith(quote_line) for quote_line in lines_to_put_in_quotes]):
            modified_lines.append(f'{replaced_kword}: "{text}"'.strip())
        else:
            modified_lines.append(f"{replaced_kword} {text}".strip())
    return "\n".join(modified_lines)


def adjust_episode_context(context: List[str]) -> List[str]:
    # For SummaryQA, we need to remove the last _partner_say.
    lines = [line for c in context for line in c.split("\n")]
    if lines[-1].startswith("_partner_say"):
        lines = lines[:-1]
    return lines


def main(opt):
    # Load the episodes.
    episodes = _create_task_agents(opt)[0].episodes
    end_episode_idx = (
        len(episodes) if opt["end_episode_idx"] <= 0 else opt["end_episode_idx"]
    )
    start_episode_idx = opt["start_episode_idx"]
    episodes = episodes[start_episode_idx:end_episode_idx]

    # Load the models.
    question_generator = QuestionGenerator(device=opt["device"])
    summary_model = SummarizationModel(device=opt["device"])

    result = []

    for episode_idx, episode in enumerate(tqdm(episodes)):
        episode_context = []
        for entry_idx, entry in enumerate(episode):
            episode_context.append(entry["text"])
            context_lines = adjust_episode_context(episode_context)
            history = generate_history(context_lines)

            # Generate summary based on the history.
            summary = summary_model(history)

            # Generate question based on the summary of the history.
            out = question_generator.extract_answers_and_generate_questions(
                context=summary,
                stop_after=1,
                blocked_answers=list(extract_persona_names(context_lines)),
            )

            if out:
                # Add to dataset as flat episodes with text=context+question and
                # labels=answers, episode_idx, entry_idx.
                text = "\n".join(context_lines + [f'_partner_say {out[0]["question"]}'])
                labels = [out[0]["answer"].lower()]
                result.append(
                    {
                        "episode_idx": episode_idx + start_episode_idx,
                        "entry_idx": entry_idx,
                        "text": text,
                        "labels": labels,
                        "episode_done": True,
                    }
                )

            if opt["verbose"]:
                print(result[-1]["text"], "\n\t", result[-1]["labels"][0], "\n")

    if opt["save_path"]:
        fname = f'{opt["task"]}_summaryqa2_{opt["datatype"]}_{opt["start_episode_idx"]}-{opt["end_episode_idx"]}'
        save_json(result, os.path.join(opt["save_path"], fname))


class CreateSummaryQA(ParlaiScript):
    @classmethod
    def setup_args(cls):
        return setup_args()

    def run(self):
        return main(self.opt)


if __name__ == "__main__":
    CreateSummaryQA.main()
