import json
import pika
import uuid

from flask import current_app

from app.tokens import generate_confirmation_token
from app.utils import urlsafe_base64_encode, force_bytes


def send_verification_email(person):
    email = person.get('email')
    first_name = person.get('first_name')
    last_name = person.get('last_name')
    token = generate_confirmation_token(email)
    uid = urlsafe_base64_encode(force_bytes(person.get('entity_id')))
    confirmation_link = current_app.config.get('FRONTEND_URL') + '/session/login/' + token + '/' + uid
    data = {
        'email_data': {
            'email_type': 'WELCOME_EMAIL',
            'recipient_email': email,
            'recipient_name': f'{first_name} {last_name}',
            'subject': 'Welcome',
            'confirmation_link': confirmation_link,
            'password_reset_url': ''
        }
    }
    send_task('email', 'send_email', data)


def send_task(queue_name, task_name, message, args=[], exchange_name=None, routing_key=None, exchange_type='direct'):
    """
    Send task to Celery using the following parameters. You can get parameters from Celery logs:
     [queues]
    .> email            exchange=email(direct) key=email
    [tasks]
       . send_email

    :queue_name: queue_name where the task is to be sent.
    :param task_name: Name of a task registered in Celery worker.
    :param message: The message (kwargs in terms of Celery) to be sent to the Celery task
    :param args: args that need to be sent to Celery task
    :param exchange_name: Celery exchange name, defaults to queue_name if not specified
    :param routing_key: The routing key which routes message to a queue from exchange, defaults to queue_name if not specified
    :param exchange_type: Type of exchange. (direct, etc.)
    :return:
    """

    if not exchange_name:
        exchange_name = queue_name
    if not routing_key:
        routing_key = queue_name

    parameters = pika.ConnectionParameters(
        host=current_app.config['BROKER_PATH'].split(':')[0],
        port=current_app.config['BROKER_PATH'].split(':')[1],
        virtual_host=current_app.config['RABBITMQ_VHOST'],
        credentials=pika.credentials.PlainCredentials(
            username=current_app.config['RABBITMQ_USER'],
            password=current_app.config['RABBITMQ_PASSWORD']
        )
    )
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=True)
    message = {
        'task': task_name,
        'id': uuid.uuid4().hex,
        'args': args,
        'kwargs': message,
    }
    properties = pika.BasicProperties(
        headers={
            'id': message['id'],
            'task': task_name,
            'argsrepr': repr(args),
        },
        content_type="application/json",
        content_encoding='utf-8'
    )
    channel.basic_publish(
        exchange=exchange_name,
        routing_key=routing_key,
        body=json.dumps(message).encode(),
        properties=properties)
    connection.close()


def send_message(queue_name, data):
    parameters = pika.ConnectionParameters(
        host=current_app.config['BROKER_PATH'].split(':')[0],
        port=current_app.config['BROKER_PATH'].split(':')[1],
        virtual_host=current_app.config['RABBITMQ_VHOST'],
        credentials=pika.credentials.PlainCredentials(
            username=current_app.config['RABBITMQ_USER'],
            password=current_app.config['RABBITMQ_PASSWORD']
        )
    )
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=json.dumps(data),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ),
    )
    print(" [x] Sent message")
