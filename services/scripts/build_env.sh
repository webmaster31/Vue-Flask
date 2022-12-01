#!/bin/bash

PROJECT_SAMPLE_ENV="$1"
GIVEN_ENV="$2"
STAGE="$3"

echo "STAGE=$STAGE"
for variable in $(cut -d= -f1 "$PROJECT_SAMPLE_ENV" | awk NF | sort | uniq) ;
do
     grep "^${variable}"= "$GIVEN_ENV"
done
