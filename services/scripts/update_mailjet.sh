#!/bin/bash

if [ -z "$1" ]
  then
    echo "No stage argument supplied."
    echo "Usage: bash $0 <stage>"
    exit 1;
fi

STAGE=$1
SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"

python3 --version;
if [[ $? = 0 ]]; then
    python3 -m pip --version;
    if [[ $? = 0 ]]; then
        python3 -m pip install python-dotenv mailjet-rest
        python3 $SCRIPT_DIR/create_mailjet_templates.py $STAGE
    else
        echo "python3 pip is not installed... Exiting"
        exit 1;
    fi

else
    echo "python3 is not installed... Exiting"
    exit 1;
fi