#!/bin/sh

python3 migrate.py -rf True
python3 version.py
if [ "$FLASK_ENV" == "production" ] || [ "$FLASK_ENV" == "test" ]
then
    waitress-serve --port=5000 --call 'main:create_app'
else
    python3 main.py
fi