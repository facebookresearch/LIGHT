"""Merge the data collected through generate_data.py."""

import os
import json
from absl import flags, logging, app
from utils import save_json, load_json
from tqdm import tqdm

FLAGS = flags.FLAGS

flags.DEFINE_string('input_directory', None,
                    'The directory from which to load the raw data.')
flags.DEFINE_string(
    'output_fname',
    '/checkpoint/light/data/lightqa/lightqa-wild-plist-valid.json',
    'The file name for the output.')


def main(argv):
    # Load & merge the data.
    fnames = [os.path.join(FLAGS.input_directory, f)
              for f in os.listdir(FLAGS.input_directory)]
    data = []
    logging.info(f'Loading files from directory {FLAGS.input_directory}.')
    for fname in tqdm(fnames):
        data.extend(load_json(fname, verbose=False))

    n_questions = sum([len(d['question_answers']) for d in data])
    logging.info(f'Total of {len(data)} episodes with {n_questions} questions.')

    # Save the data.
    save_json(data, FLAGS.output_fname)
    logging.info(f'Saved to data to {FLAGS.output_fname}.')


if __name__ == '__main__':
    app.run(main)