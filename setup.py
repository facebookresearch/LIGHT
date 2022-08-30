#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from setuptools import setup, find_packages
import sys

if sys.version_info < (3, 6):
    sys.exit("Sorry, Python >=3.6 is required for ParlAI.")

with open("README.md", encoding="utf8") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

with open("requirements.txt") as f:
    reqs = f.read()

# TODO ParlAI is a requirement for LIGHT, must make sure it's cloned and setup.py first
try:
    import parlai
except:
    print(
        "ParlAI must be installed to use LIGHT, please clone the repo and run setup.py develop"
    )

if __name__ == "__main__":
    setup(
        name="light",
        version="0.1",
        description="Text-Adventure Game Research Platform.",
        long_description=readme,
        # url='http://light-game.ai/',
        license=license,
        python_requires=">=3.6",
        packages=find_packages(
            exclude=(
                "data",
                "scripts",
                "tests",
                "light_internal",
            )
        ),
        install_requires=reqs.strip().split("\n"),
        include_package_data=True,
        entry_points={
            "console_scripts": ["light=light.light_cli:main"],
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",
            "Natural Language :: English",
        ],
    )
