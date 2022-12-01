from app import celery_app
from lib.clickwrap_s3 import dump_clickwrap_to_s3

@celery_app.task(name='dump_clickwrap_acceptance')
def dump_clickwrap_acceptance(**message):
    return dump_clickwrap_to_s3(message)
