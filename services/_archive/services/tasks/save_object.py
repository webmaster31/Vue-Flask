from app import celery_app
from lib.models import get_class_from_string
import logging

@celery_app.task(name='save_object')
def save_object(**message):
    """
    Save the data to database
    :key of message is ClassName
    :param message: dict: {
        'ClassName1': {
            'data_type_parameter': value,
            ...
        },
        'ClassName2': {
            'data_type_parameter': value,
            ...
        }
    }
    :return:
    """
    logging.debug("save_object task parameter:")
    logging.debug(message)

    if message is None:
        message = {}

    for class_name_string in message.keys():
        class_name = get_class_from_string(class_name_string)
        class_object = class_name(**message[class_name_string])
        class_object.save()
