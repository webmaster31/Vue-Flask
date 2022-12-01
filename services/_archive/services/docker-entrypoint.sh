#!/bin/sh

python3 version.py
celery -A app worker -Q save,save-notification,email,dump-clickwrap --loglevel=info --uid=nobody --gid=nogroup