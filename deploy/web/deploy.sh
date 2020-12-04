#!/bin/bash
# Script to build and run the server
WEBDIR="$(dirname "${BASH_SOURCE[0]}")"  # get the directory name
WEBDIR="$(realpath "${WEBDIR}")"    # resolve its full path if need becd $WEBDIR
SERVER_FILE="${WEBDIR}/server/run_server.py"
BUILD_SCRIPT="${WEBDIR}/build.sh"


if [ -n "$2" ];
then
  bash $BUILD_SCRIPT $1
fi

if [ -z "$1" ];
then
  echo "Must provide a config name from configs as an argument"
  cd "configs"
  ls
  exit 1
fi

CONF_FN=$WEBDIR"/configs/"$1"/config"

python $SERVER_FILE @$CONF_FN
