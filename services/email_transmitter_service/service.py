import sys
import json
import time
import pika


from utils.log_config import logger
from transmitters.ses import SesTransmitter
from transmitters.mailjet import MailjetTransmitter

provider_transmitter_map = {
    'ses': SesTransmitter,
    'mailjet': MailjetTransmitter
}


DEV_MODE = False

def rabbitmq_consumer(message, transmitter, retry_count=5, retry_interval=10):
    while retry_count > 0:
        try:
            body = json.loads(message)
            event = body['event']
            data = body['data']
            to_emails = body['to_emails']
            transmitter.handle_event(event, data, to_emails)
        except Exception as e:
            retry_count -= 1
            logger.warning(f"{retry_count} retries left for message {str(message)}")
            if retry_count > 0:
                time.sleep(retry_interval)
            else:
                logger.log_uncaught_exception(service='upload_processor', isRaise=False,
                                              message=f"Retry limit exceeded for message {str(message)}")



if __name__ == "__main__":
    try:
        version_file = open("version", "r")
        version = version_file.read().strip()
    except:
        logger.log_uncaught_exception(False, message="Unable to read version.")
        version = "Unknown"
    
    logger.info(f"Running email_transmitter version: {version}")

    args = sys.argv
    if len(args) < 2:
        logger.error("Stage option not specified.")
        sys.exit(1)

    if DEV_MODE:
        logger.info("Running with DEV_MODE = True")
        provider = 'mailjet'
        event = "USER_CREATED"
        event_data = {"confirmation_link": "https://google.com", "recipient_name": "Test User"}
        to_addresses = ["asymlabs@gmail.com"]
        transmitter_class = provider_transmitter_map.get(provider)
        transmitter = transmitter_class()
        transmitter.handle_event(event, event_data, to_addresses)
        sys.exit(0)
        
    import settings
    from utils.queue import Queue

    settings.stage = args[1]

    transmitter_class = provider_transmitter_map.get(settings.provider)
    if not transmitter_class:
        raise Exception('EMAIL_PROVIDER environment variable is not set or not supported. ' +
                        f'Valid values: {", ".join(provider_transmitter_map.keys())}')

    transmitter = transmitter_class()


    while True:
        try:
            stage = args[1]
            logger.debug(f'Listening to queue {settings.email_transmitter_queue_name} on host: {settings.rabbitmq_host}')
            email_transmitter_queue = Queue(settings.email_transmitter_queue_name, host=settings.rabbitmq_host)
            consumer = lambda message: rabbitmq_consumer(message, transmitter)
            email_transmitter_queue.consume(consumer, threaded=True, num_threads=1)
            break
        except (pika.exceptions.IncompatibleProtocolError, pika.exceptions.AMQPConnectionError, pika.exceptions.ConnectionClosedByBroker):
            logger.warn("RabbitMQ Connection is closed.")
            print("Unable to connect. Retrying after 60 seconds.")
            time.sleep(60)
        except:
            logger.log_uncaught_exception(isRaise=False)
