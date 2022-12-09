
# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/bin/bash
# Script to build the server by running both npm commands
WEBDIR="$(dirname "${BASH_SOURCE[0]}")"  # get the directory name
WEBDIR="$(realpath "${WEBDIR}")"    # resolve its full path if need becd $WEBDIR
BUILDER_DIR="${WEBDIR}/builderapp/"
GAME_DIR="${WEBDIR}/gameapp/"
LANDING_DIR="${WEBDIR}/landingapp/"
SERVER_FILE="${WEBDIR}/server/run_server.py"

CONF_FN="./configs/"$1".js"

if [ -z "$1" ];
then
  echo "Must provide a config name from configs as an argument"
  cd "configs"
  ls
  exit 1
fi

cp $CONF_FN $BUILDER_DIR"src/config.js"
cp $CONF_FN $LANDING_DIR"src/config.js"
cp $CONF_FN $GAME_DIR"src/config.js"

mkdir build
cd $BUILDER_DIR
npm install
CI=false npm run build
cd $GAME_DIR
npm install
CI=false npm run build
cd $LANDING_DIR
npm install
CI=false npm run build
