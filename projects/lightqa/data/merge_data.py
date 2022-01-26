"""Merge the data collected through generate_data.py."""

import os
from absl import flags, logging, app
from parlai_internal.projects.light.lightqa.data.utils import save_json, load_json
from tqdm import tqdm

FLAGS = flags.FLAGS

flags.DEFINE_string(
    "input_directory", None, "The directory from which to load the raw data."
)
flags.DEFINE_string(
    "output_path",
    "/checkpoint/light/data/lightqa/summaryqa2/",
    "The path name for the output.",
)
flags.DEFINE_string("name", "light_dialog_wild_summaryqa2", "The name of the dataset.")


def main(argv):
    # Load & merge the data.
    fnames = [
        os.path.join(FLAGS.input_directory, f)
        for f in os.listdir(FLAGS.input_directory)
        if f.startswith(FLAGS.name)
    ]

    logging.info(f"Trying to load files from directory {FLAGS.input_directory}.")
    for datatype in ["train", "valid", "test"]:
        fnames_dt = list(filter(lambda f: datatype in f.split("/")[-1], fnames))
        if not fnames_dt:
            logging.info(f'No data for datatype "{datatype}".')
            continue
        data = []
        for fname in tqdm(fnames_dt, desc=f'Loading "{datatype}"'):
            data.extend(load_json(fname, verbose=False))

        logging.info(f'Total of {len(data)} episodes for datatype "{datatype}".')

        # Save the data.
        output_fname = os.path.join(FLAGS.output_path, f"{FLAGS.name}_{datatype}.json")
        save_json(data, output_fname)


if __name__ == "__main__":
    app.run(main)
