#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from typing import Dict, Union, List, Any
from collections import defaultdict
import parlai.utils.logging as logging
from parlai.crowdsourcing.utils.analysis import AbstractResultsCompiler
from mephisto.abstractions.providers.mturk.utils.script_utils import (
    get_mturk_ids_from_unit_id,
)
from mephisto.abstractions.databases.local_database import LocalMephistoDB


db = LocalMephistoDB()


def last_n_tasks(n=20, name_part=""):
    tasks = [t.task_name for t in db.find_tasks() if name_part in t.task_name]
    return tasks[-n:]


def get_last_submission(submissions):
    last_submit_time = 0
    last_submission = None
    for submission in submissions:
        messages = submission['data']['messages']
        submit_time = messages[-1]['timestamp']
        if submit_time > last_submit_time and submission['data'].get('save_data', None):
            last_submit_time = submit_time
            last_submission = submission
    return last_submission


def is_chat_message(message):
    msg_id = message.get('id', None)
    return (
        msg_id != 'Coordinator' and msg_id != 'SUBMIT_WORLD_DATA' and 'text' in message
    )


def format_message(message):
    dic = {}
    dic['speaker'] = message['id']
    dic['text'] = message['text']
    dic['timestamp'] = message['timestamp']
    return dic


class MultiPartyChatResultsCompiler(AbstractResultsCompiler):
    """
    Compiles the results of Multi-Party Chat crowdsourcing task into a json dataset.
    """

    def __init__(self, opt):
        super().__init__(opt)
        self._task_name = opt['task_name']

    def is_unit_acceptable(self, unit_data):
        raw_messages = list(filter(is_chat_message, unit_data['data']['messages']))
        messages = list(map(format_message, raw_messages))
        return len(messages) > 0

    def get_task_data(self) -> List[Dict[str, Any]]:
        """
        Retrieves task data for a list of Mephisto task units.
        """
        task_data = []
        for unit in self.get_task_units():
            unit_data = self.get_data_from_unit(unit)
            if unit_data and self.is_unit_acceptable(unit_data):
                db = self.get_mephisto_db()
                mturk_ids = get_mturk_ids_from_unit_id(db, unit.db_id)
                unit_data['mturk_ids'] = mturk_ids

                task_data.append(unit_data)

        return task_data

    def get_results_path_base(self):
        return os.path.join(self.output_folder, self._task_name)

    def compile_results(self) -> Dict[str, Dict[str, Union[dict, str]]]:
        logging.info('Retrieving task data from Mephisto.')
        task_units = self.get_task_data()
        logging.info(f'Data for {len(task_units)} units loaded successfully.')

        dialogs = defaultdict(list)
        results = {}

        for work_unit in task_units:
            assignment_id = work_unit['assignment_id']
            dialogs[assignment_id].append(work_unit)

        for assignment_id, submissions in dialogs.items():
            if len(submissions) != 3:

                logging.warning(
                    f'Skipping assignment {assignment_id} with incomplete data. Only {len(submissions)} out of 3 workers have submitted.'
                )
                continue

            submission = get_last_submission(submissions)
            if not submission:
                logging.warning(
                    f'Skipping assignment {assignment_id} because there was no saved data'
                )
                continue
            raw_messages = list(filter(is_chat_message, submission['data']['messages']))
            messages = list(map(format_message, raw_messages))

            ret = {}
            ret['messages'] = messages

            save_data = submission['data'].get('save_data', None)

            if save_data:
                ret['graph'] = save_data['graph']
                ret['characters'] = save_data['characters']
                ret['location'] = save_data['location']

            ret['worker_mturk_ids'] = {}
            ret['disqualify_reaons'] = {}
            ret['form_responses'] = {}
            for submission in submissions:
                agent_name = submission['data']['agent_name']
                if save_data:
                    disqualify_reason = submission['data']['save_data'].get(
                        'disqualify_reason', None
                    )
                    ret['disqualify_reaons'][agent_name] = disqualify_reason

                ret['worker_mturk_ids'][agent_name] = submission['mturk_ids']

                final_submission = submission['data'].get('final_submission', None)
                if final_submission:
                    try:
                        ret['form_responses'][agent_name] = final_submission[
                            'task_data'
                        ]['form_responses']
                    except TypeError:
                        logging.warning(
                            f"Malformed data in form response for agent {agent_name} (MTurk ID: {submission['mturk_ids']}): {final_submission}"
                        )

            task_duration = submission['task_end'] - submission['task_start']
            ret['task_duration'] = task_duration
            if len(messages) > 0 or True:
                results[assignment_id] = ret

        logging.info(f'{len(results)} dialogues compiled.')
        return results


def main():
    parser = MultiPartyChatResultsCompiler.setup_args()
    args = parser.parse_args()

    if not args.task_name:
        print("Most recent task names:")
        for t in last_n_tasks(name_part=""):
            print(f"\t{t}")

        task_name = input("Insert the task name you want to compile results for: ")

    opt = {
        'task_name': args.task_name if args.task_name else task_name,
        'results_format': 'json',
        'output_folder': args.output_folder,
        'database_path': None,
    }
    data_compiler = MultiPartyChatResultsCompiler(opt)
    data_compiler.compile_and_save_results()


if __name__ == "__main__":
    main()
