"""Transform the collected data to a ParlAI dataset format."""

from absl import flags, logging, app
from typing import List, Dict, Any
from tqdm import tqdm

from generate_data import DialogueLoader
from utils import load_json, save_json

FLAGS = flags.FLAGS

flags.DEFINE_string('input_fname',
                    '/checkpoint/light/data/lightqa/lightqa-wild-plist-test.json',
                    'Name of the input file.')
flags.DEFINE_string('output_fname',
                    '/checkpoint/light/data/lightqa/lightqa-wild-{}-{}.json',
                    'Name of the output file with placeholders for dataname and'
                    ' datatype.')


def generate_summary_qa_data(data: List[Dict[str, Any]]
                             ) -> List[Dict[str, str]]:
    result = []
    logging.info('Generating summary qa data.')
    for episode in tqdm(data):
        partner_name = [p for p in episode['paragraph_list']
                     if p['type'] == '_partner_name'][0]['text']
        history = episode['history'][0]
        summary = episode['summary']
        for qa in episode['question_answers']:
            question = qa['question']
            answer = qa['answer']
            answer_sentence = qa['answer_sentence']
            result.append({
                'text': f'{history}\n{partner_name}: "{question}"',
                'knowledge_response_answer': answer,
                'knowledge_response_sentence': answer_sentence,
                'summary': summary,
            })
    return result


def generate_overlap_qa_data(data: List[Dict[str, Any]]
                             ) -> List[Dict[str, str]]:
    result = []
    logging.info('Generating overlap qa data.')
    for episode in tqdm(data):
        paragraphs = episode['paragraph_list']
        self_name = [p for p in episode['paragraph_list']
                     if p['type'] == '_self_name'][0]['text']

        for paragraph in paragraphs:
            overlaps = paragraph['matching_words_overlap']
            if overlaps and 'say' in paragraph['type']:
                for match, ids_and_match_sentences in overlaps.items():
                    # Only consider mentions in paragraphs earlier than the last one.
                    # ids_and_match_sentences = list(filter(
                    #     lambda x: (paragraph['id'] - x[0]) > 1, ids_and_match_sentences))

                    # Only consider mentions where somebody/something else mentioned the match.
                    ids_and_match_sentences = list(filter(
                        lambda x: paragraph['type'] != {p['id']: p for p in paragraphs}[x[0]]['type'], ids_and_match_sentences))

                    # Only consider mentions from humans (i.e., self_say).
                    ids_and_match_sentences = list(filter(
                        lambda x: paragraph['type'] == '_self_say', ids_and_match_sentences))

                    if not ids_and_match_sentences:
                        continue   
                    _, match_sentences = zip(*ids_and_match_sentences)
                    match_str = match if isinstance(match, str) else ' '.join(match)
                    history = DialogueLoader.generate_history(paragraphs[:paragraph['id']])

                    result.append({
                        'text': history,
                        'knowledge_response_answer': match_str,
                        'knowledge_response_sentence': '\t'.join(match_sentences),
                        'dialogue_response': f'{self_name}: "{paragraph["text"]}"',
                    })

    return result
    

def main(argv):
    data = load_json(FLAGS.input_fname)
    datatype = FLAGS.input_fname.split('/')[-1].split('.')[0].split('-')[-1]

    # Generate lightqa-summary.
    summary_qa_data = generate_summary_qa_data(data)
    save_json(summary_qa_data, FLAGS.output_fname.format('summary', datatype))

    # Generate lightqa-overlap.
    overlap_qa_data = generate_overlap_qa_data(data)
    save_json(overlap_qa_data, FLAGS.output_fname.format('overlap', datatype))
    

if __name__ == "__main__":
    app.run(main)