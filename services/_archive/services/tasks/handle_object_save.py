from app import celery_app
from lib import models
import logging

@celery_app.task(name='handle_object_save')
def handle_object_save(table_name, operation, **message):
    """
    This task will receive all object saves and 'operation' parameter is either equal to 'created' or 'updated'.
    Handle any object save notifications in this task.
    """
    logging.debug("handle_object_save task parameters:")
    logging.debug(table_name)
    logging.debug(operation)
    logging.debug(message)
