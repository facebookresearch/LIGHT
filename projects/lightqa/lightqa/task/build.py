#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Download and build the data if it does not exist.
"""

from parlai.core.build_data import DownloadableFile
import parlai.core.build_data as build_data
import os
from shutil import copyfile


RESOURCES = [
    DownloadableFile(
        "/checkpoint/light/data/lightqa/lightqa-wild-overlap-train.json",
        "lightqa-wild-overlap-train.json",
        "093f2547444ad7b60cd590bbb857e4b606d73128d11573fff8feee43ebf17177",
        zipped=False,
    ),
    DownloadableFile(
        "/checkpoint/light/data/lightqa/lightqa-wild-overlap-valid.json",
        "lightqa-wild-overlap-valid.json",
        "845a4ab72815cab01fd1e8a9a0a87ad3e9c52f43dc4576159e7c9659c40d7cc4",
        zipped=False,
    ),
    DownloadableFile(
        "/checkpoint/light/data/lightqa/lightqa-wild-overlap-test.json",
        "lightqa-wild-overlap-test.json",
        "b17bb73b5c7b78eeedc8af9f5e10b33de2c7c6465ff8651fa0504f90543a2489",
        zipped=False,
    ),
    DownloadableFile(
        "/checkpoint/light/data/lightqa/lightqa-wild-summary-train.json",
        "lightqa-wild-summary-train.json",
        "9e9275b7321d432d1e56e7986512a7a103476d7c2ce14f6937a2b16299025da0",
        zipped=False,
    ),
    DownloadableFile(
        "/checkpoint/light/data/lightqa/lightqa-wild-summary-valid.json",
        "lightqa-wild-summary-valid.json",
        "81523901d39bc218af4f5df7f3d90a31610cddc5faf332be321d32fe8ef4d0a3",
        zipped=False,
    ),
    DownloadableFile(
        "/checkpoint/light/data/lightqa/lightqa-wild-summary-test.json",
        "lightqa-wild-summary-test.json",
        "4554e20b384faba1b16ec1a96afa14fbb631679ac1582f542e8d1826ee8f31f9",
        zipped=False,
    ),
    DownloadableFile(
        "/checkpoint/light/data/lightqa/summaryqa2/light_dialog_wild_summaryqa2_train.json",
        "lightqa-wild-summaryqa2-train.json",
        "0c618e0736317fbb9a688f82777165675b5967ffc5208041da940a3e3a947d25",
        zipped=False,
    ),
    DownloadableFile(
        "/checkpoint/light/data/lightqa/summaryqa2/light_dialog_wild_summaryqa2_valid.json",
        "lightqa-wild-summaryqa2-valid.json",
        "3646ff1e6549ec82588caaf7da998ef18df629cacdde43d8ce813df545aabe6c",
        zipped=False,
    ),
    DownloadableFile(
        "/checkpoint/light/data/lightqa/summaryqa2/light_dialog_wild_summaryqa2_test.json",
        "lightqa-wild-summaryqa2-test.json",
        "70804bd77fe7568326a1e229b3ece578cd1867c3e0e8a14fef23faf4e2032f14",
        zipped=False,
    ),
    DownloadableFile(
        "/checkpoint/light/data/lightqa/lightqa-wild-overlapdialogue-train.json",
        "lightqa-wild-overlapdialogue-train.json",
        "4808e74eabbdd8a7df85db25003960b7be3ef580bc7ff783a591a8be1a4b5488",
        zipped=False,
    ),
    DownloadableFile(
        "/checkpoint/light/data/lightqa/lightqa-wild-overlapdialogue-valid.json",
        "lightqa-wild-overlapdialogue-valid.json",
        "461d8331cdbbe4d0a14c2ebed5ae058bb571657d4cbc8bb97c3524230e0724b1",
        zipped=False,
    ),
    DownloadableFile(
        "/checkpoint/light/data/lightqa/lightqa-wild-overlapdialogue-test.json",
        "lightqa-wild-overlapdialogue-test.json",
        "ed19a7f6d0df558c54e555bff3bb22e6f1e78cb6022d363b90091e949b4cc177",
        zipped=False,
    ),
]


def build(opt):
    version = "v1.1.0"
    dpath = os.path.join(opt["datapath"], "lightqa")

    if not build_data.built(dpath, version):
        print("[building data: " + dpath + "]")
        if build_data.built(dpath):
            # An older version exists, so remove these outdated files.
            build_data.remove_dir(dpath)
        build_data.make_dir(dpath)

        # Download the data.
        for downloadable_file in RESOURCES:
            if downloadable_file.url.startswith("/checkpoint"):
                copyfile(
                    downloadable_file.url,
                    os.path.join(dpath, downloadable_file.file_name),
                )
            else:
                downloadable_file.download_file(dpath)

        # Mark the data as built.
        build_data.mark_done(dpath, version)
