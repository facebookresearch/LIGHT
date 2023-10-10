import json
import collections
import numpy as np

from absl import app, flags
from parlai.utils.io import PathManager

FLAGS = flags.FLAGS

flags.DEFINE_string(
    "data_path",
    "/private/home/ladolphs/code/ParlAI/data/wizard_of_wikipedia/train.json",
    "Path to the json data.",
)


def main(argv):
    # Load data.
    with PathManager.open(FLAGS.data_path) as f:
        data = json.load(f)

    # Collect length values.
    stats = collections.defaultdict(list)
    for conversation in data:
        dialogue = conversation["dialog"]
        for speak_act in dialogue:
            if (
                "wizard" in speak_act["speaker"].lower()
                and "checked_sentence" in speak_act
                and speak_act["checked_sentence"]
            ):

                checked_sentence_length = len(
                    list(speak_act["checked_sentence"].values())[0].split()
                )
                stats["checked_sentence_length"].append(checked_sentence_length)
                if "no_passages_used" not in speak_act["checked_sentence"]:
                    stats["checked_sentence_length_corrected"].append(
                        checked_sentence_length
                    )

                stats["text_length"].append(len(speak_act["text"].split()))

    # Functions to compute on top of length values.
    results = {}
    fn_to_apply = {
        "mean": np.mean,
        "median": np.median,
        "min": np.min,
        "max": np.max,
        "frac_above_10": lambda arr: sum(x >= 10 for x in arr) / len(arr),
        "frac_above_20": lambda arr: sum(x >= 20 for x in arr) / len(arr),
    }

    # Apply functions and print results.
    print(f"Results for {FLAGS.data_path}")
    for k, v in stats.items():
        results[k] = {}
        print(k)
        for fn_name, fn in fn_to_apply.items():
            results[k][fn_name] = fn(v)
            print(f"\t{fn_name}: {results[k][fn_name]:.2f}")
        print()


if __name__ == "__main__":
    app.run(main)
