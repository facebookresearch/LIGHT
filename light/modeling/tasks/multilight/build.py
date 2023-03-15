#!/usr/bin/env python3

# Copyright (c) Meta, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
# Download and build the data if it does not exist.

import os
import shutil
import parlai.core.build_data as build_data
import parlai.utils.logging as logging

from light.modeling.tasks.multilight import constants

def build(opt):
    dpath = os.path.join(opt['datapath'], constants.DATASET_NAME)
    logging.warning('Using fake build method. Update with the final.')
    version = '0.1'
    if not build_data.built(dpath, version):
        logging.info(
            f'[building data: {dpath}]\nThis may take a while but only heppens once.'
        )
        if build_data.built(dpath):
            # An older version exists, so remove these outdated files.
            build_data.remove_dir(dpath)
        build_data.make_dir(dpath)

        # Download the data.
        # TODO: Add the dataset files to the S3 bucket for download.
        # DATASET_FILE.download_file(dpath)
        for f in ('train', 'valid', 'test'):
            fname = f'{f}.jsonl'
            srouce = os.path.join('/private/home/komeili/dev/ParlAI/data/light_multiparty/', fname)
            dest = os.path.join(dpath, fname)
            shutil.copyfile(srouce, dest)
        logging.info('Finished downloading dataset files successfully.')

        build_data.mark_done(dpath, version)
