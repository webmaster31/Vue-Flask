#!/bin/bash

set +ex

CLEAR='\033[0m'
RED='\033[0;31m'

function usage() {
  if [ -n "$1" ]; then
    echo -e "${RED} 👉 $1${CLEAR}\n";
  fi
  echo "Usage: $0 [-e env] [-u run-ui]"
  echo "  -e, --env             Environment to run (dev, test, production)"
  echo "  -u, --run-ui          Run UI app (Optional argument)(Default Value: false)"
  echo ""
  echo "Example: $0 --env test --run-ui false"
  exit 1
}

# parse params
while [[ "$#" -gt 0 ]]; do case $1 in
  -e|--env) ENV="$2"; shift;shift;;
  -u|--run-ui) RUN_UI="$2"; shift;shift;;
  *) usage "Unknown parameter passed: $1"; shift; shift;;
esac; done

# verify params
if [ -z "$ENV" ]; then usage "Environment is not provided"; fi;
if [ -z "$RUN_UI" ]; then RUN_UI=false; fi;

export SERVICE_ROOT="${PWD}"
cd ..
export PROJECT_ROOT="${PWD}"
export API_ROOT="$PROJECT_ROOT"/flask
export VUE_ROOT="$PROJECT_ROOT"/vue

cd "$API_ROOT" || { echo "No flask folder found inside $PROJECT_ROOT"; exit 1; }
if [ "$RUN_UI" == true ]; then
  cd "$VUE_ROOT" || { echo "No vue folder found inside $PROJECT_ROOT"; exit 1; }
fi;

# copy provided env to all folders
cp "$SERVICE_ROOT/$ENV.env" "$API_ROOT/temp.env" &> /dev/null  || { echo  -e "${RED} 👉 No $ENV.env found inside $SERVICE_ROOT\n"; exit 1; }
cp "$SERVICE_ROOT/$ENV.env" "$SERVICE_ROOT/temp.env";
if [ "$RUN_UI" == true ]; then
  cp "$SERVICE_ROOT/$ENV.env" "$VUE_ROOT/temp.env";
fi;

# validate env files
bash "$SERVICE_ROOT/scripts/validate_env.sh" "$SERVICE_ROOT/.env.dev" "$SERVICE_ROOT/temp.env"; exit_status_service=$?
bash "$SERVICE_ROOT/scripts/validate_env.sh" "$API_ROOT/.env.dev" "$API_ROOT/temp.env"; exit_status_api=$?

exit_status_ui=0
if [ "$RUN_UI" == true ]; then
  bash "$SERVICE_ROOT/scripts/add_duplicate_variables.sh" "$VUE_ROOT/temp.env"
  bash "$SERVICE_ROOT/scripts/validate_env.sh" "$VUE_ROOT/.env.example" "$VUE_ROOT/temp.env"; exit_status_ui=$?;
fi;

if [ $exit_status_service -eq 1 ] || [ $exit_status_api -eq 1 ] || [ $exit_status_ui -eq 1 ]; then
  echo -e "${RED} 👉 Correct the provided env file. Exiting now !!!! ${CLEAR}\n";
  exit 1
fi;

echo "Validation of env variables complete"

# update env files
rm -rf "$SERVICE_ROOT"/.env || true
bash "$SERVICE_ROOT"/scripts/build_env.sh "$SERVICE_ROOT/.env.dev" "$SERVICE_ROOT/temp.env" "$ENV" >> "$SERVICE_ROOT"/.env

rm -rf "$API_ROOT"/.env || true
bash "$SERVICE_ROOT"/scripts/build_env.sh "$API_ROOT/.env.dev" "$API_ROOT/temp.env" "$ENV" >> "$API_ROOT"/.env

if [ "$RUN_UI" == true ]; then
  rm -rf "$VUE_ROOT"/.env || true
  bash "$SERVICE_ROOT"/scripts/build_env.sh "$VUE_ROOT"/.env.example "$VUE_ROOT/temp.env" "$ENV"  >> "$VUE_ROOT"/.env;
fi;

rm -rf "$API_ROOT/temp.env" || true
rm -rf "$SERVICE_ROOT/temp.env" || true
if [ "$RUN_UI" == true ]; then
  rm -rf "$VUE_ROOT/temp.env" || true
fi;

echo "Building env files complete"

cd "$SERVICE_ROOT" ||  { echo "No service folder found"; exit 1; }

# run docker compose
docker-compose -f docker-compose.yml up -d --build

# run UI app
if [ "$RUN_UI" == true ]; then
  cd "$VUE_ROOT" || { echo "No vue folder found inside $PROJECT_ROOT"; exit 1; }
  npm install --save vue-moment
  if [ "$ENV" == "production" ];
  then
    npm install
    npm run build
  else
    npm install
    npm run serve
  fi;
fi;


