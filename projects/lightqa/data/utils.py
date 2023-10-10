"""Utils for data handling."""
from absl import logging
import json
import spacy

from string import punctuation
from nltk.corpus import stopwords

# ! python -m spacy download en_core_web_sm
nlp = spacy.load("en_core_web_sm")
STOP_WORDS = stopwords.words("english")
PUNCTUATION = set(punctuation)


def save_json(data, fname, verbose=True):
    if not fname.endswith(".json"):
        fname += ".json"
    if verbose:
        logging.info(f"Save to {fname}.")
    with open(fname, "w") as f:
        json.dump(data, f)


def load_json(fname, verbose=True):
    if verbose:
        logging.info(f"Load data from {fname}.")
    with open(fname, "r") as f:
        data = json.load(f)
    return data


def extract_entities(
    sentence, pos=("PROPN", "NOUN"), use_named_entities=True, use_noun_chunks=True
):
    doc = nlp(sentence)
    results = []
    if pos:
        for token in doc:
            if token.pos_ in pos:
                results.append(token)
    if use_named_entities:
        for ent in doc.ents:
            results.append(ent)
    if use_noun_chunks:
        for chunk in doc.noun_chunks:
            if chunk.text.lower() not in STOP_WORDS:
                results.append(chunk)
    results = list(set([r.text for r in results]))
    return results
