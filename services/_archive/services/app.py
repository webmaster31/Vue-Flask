import logging
import os

import rollbar
from celery import Celery
from celery.signals import task_failure
from dotenv import load_dotenv
from rollbar.logger import RollbarHandler

load_dotenv()

STAGE = os.environ.get('STAGE')
BROKER_PATH = os.environ.get('BROKER_PATH', 'host.docker.internal:5672')
RABBITMQ_USER = os.environ.get('RABBITMQ_USER')
RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD')
RABBITMQ_VHOST = os.environ.get('RABBITMQ_VHOST')

ROLLBAR_ACCESS_TOKEN = os.environ.get('ROLLBAR_ACCESS_TOKEN')

rollbar.init(ROLLBAR_ACCESS_TOKEN, STAGE, allow_logging_basic_config=False)


def _create_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    rollbar_handler = RollbarHandler(ROLLBAR_ACCESS_TOKEN, 'development')
    rollbar_handler.setLevel(logging.WARNING)
    logger.addHandler(rollbar_handler)
    return logger


def celery_base_data_hook(request, data):
    data['framework'] = 'celery'


rollbar.BASE_DATA_HOOK = celery_base_data_hook

celery_app = Celery(
    broker=f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{BROKER_PATH}/{RABBITMQ_VHOST}',
    broker_connection_max_retries=30,
    backend='rpc://',
    include=['tasks']
)
celery_app.config_from_object('celery_app_config')

logger = _create_logger()


@task_failure.connect
def handle_task_failure(**kw):
    rollbar.report_exc_info(extra_data=kw, level='warning')
