"""Utils for data handling."""
from absl import logging
import json
    
def save_json(data, fname, verbose=True):
    if verbose:
        logging.info(f'Save to {fname}.')
    with open(fname, 'w') as f:
        json.dump(data, f)

def load_json(fname, verbose=True):
    if verbose:
        logging.info(f'Load data from {fname}.')
    with open(fname, 'r') as f:
        data = json.load(f)
    return data