#!/bin/bash
# Script to build and run the server
WEBDIR="$(dirname "${BASH_SOURCE[0]}")"  # get the directory name
WEBDIR="$(realpath "${WEBDIR}")"    # resolve its full path if need becd $WEBDIR
SERVER_FILE="${WEBDIR}/server/run_server.py"
BUILD_SCRIPT="${WEBDIR}/build.sh"

bash $BUILD_SCRIPT
python $SERVER_FILE @$WEBDIR/config