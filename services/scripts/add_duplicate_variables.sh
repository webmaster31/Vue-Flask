#!/bin/bash

GIVEN_ENV="$1"


additional_variables_for_vue=("GITHUB_CLIENT_ID" "LINKEDIN_CLIENT_ID" "GOOGLE_CLIENT_ID" "PUSHER_API_KEY" "PUSHER_API_SECRET" "PUSHER_CLUSTER")

for variable in ${additional_variables_for_vue[*]};
do
  if grep -q "VUE_APP_$variable=" "$GIVEN_ENV"
    then
      echo "ok" >> /dev/null
    else
      value=$(grep "^${variable}"= "$GIVEN_ENV" | cut -d '=' -f 2)
      echo "VUE_APP_$variable=$value" >> "$GIVEN_ENV"
  fi
done
