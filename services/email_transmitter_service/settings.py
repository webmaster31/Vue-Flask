import os


stage = os.environ['STAGE']
rollbar_access_token = os.environ['ROLLBAR_ACCESS_TOKEN']
rabbitmq_host = os.environ['BROKER_PATH'].split(':')[0]
rabbitmq_port = int(os.environ['BROKER_PATH'].split(':')[1]) if len(os.environ['BROKER_PATH'].split(':')) > 1 else None
rabbitmq_vhost = os.getenv('RABBITMQ_VHOST') or '/'
rabbitmq_username = os.environ['RABBITMQ_USER']
rabbitmq_password = os.environ['RABBITMQ_PASSWORD']
provider = os.environ['EMAIL_PROVIDER'].strip().lower()

email_transmitter_queue_name = 'email-transmitter'
