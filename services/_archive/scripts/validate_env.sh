#!/bin/bash

PROJECT_SAMPLE_ENV="$1"
GIVEN_ENV="$2"

variables_not_found=()
need_exit=0

for variable in $(cut -d# -f1 "$PROJECT_SAMPLE_ENV" | cut -d= -f1 | awk NF | sort |uniq) ;
do
  if [[ -n "${variable//[$'\t\r\n ']}" ]];
    then
      if grep -q "$variable" "$GIVEN_ENV"
        then
            echo "ok" >> /dev/null
        else
            variables_not_found+=("$variable")
            need_exit=1
      fi
  fi
done

if [ $need_exit -eq 1 ]; then
  echo "Variables not found in provided env": "${variables_not_found[@]}"
  exit 1;
fi;
