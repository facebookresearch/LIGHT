#!/bin/bash
# Script to build the server by running both npm commands
WEBDIR="$(dirname "${BASH_SOURCE[0]}")"  # get the directory name
WEBDIR="$(realpath "${WEBDIR}")"    # resolve its full path if need becd $WEBDIR
BUILDER_DIR="${WEBDIR}/builderapp/"
GAME_DIR="${WEBDIR}/gameapp/"
SERVER_FILE="${WEBDIR}/server/run_server.py"

cd $BUILDER_DIR
npm run build
cd $GAME_DIR
npm run build
