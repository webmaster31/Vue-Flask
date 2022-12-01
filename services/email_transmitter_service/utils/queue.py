import time
import pika
import json
import threading
import functools

import settings
from utils.log_config import logger


def credentials():
    return pika.PlainCredentials(
        settings.rabbitmq_username, settings.rabbitmq_password
    )


class Consumer:
    def __init__(self, queue, host="rabbitmq"):
        vhost = settings.rabbitmq_vhost
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host, virtual_host=vhost, socket_timeout=15, credentials=credentials())
        )
        self.channel = self.connection.channel()
        self.queue = queue
        self.channel.queue_declare(queue=self.queue, durable=True)

    def consume(self, callback):
        def _callback(ch, method, properties, body):
            callback(body)
            ch.basic_ack(method.delivery_tag)

        try:
            self.channel.basic_consume(queue=self.queue, on_message_callback=_callback)
            logger.debug(f" [*] Waiting for messages from queue {self.queue}.")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Exiting gracefully..")
            self.channel.stop_consuming()
        finally:
            self.connection.close()


class ThreadedConsumer(Consumer):
    def __init__(self, queue, num_threads, host="rabbitmq"):
        super().__init__(queue, host)
        self.threads = []
        self.channel.basic_qos(prefetch_count=num_threads)

    def _ack_message(self, ch, delivery_tag):
        if ch.is_open:
            ch.basic_ack(delivery_tag)
        else:
            # Channel is already closed, so we can't ACK this message;
            # log and/or do something that makes sense for your app in this case.
            pass

    def _do_work(self, ch, delivery_tag, body, callback):
        try:
            thread_id = threading.get_ident()
            logger.info(
                "Thread id: %s Delivery tag: %s Message body: %s",
                thread_id,
                delivery_tag,
                body,
            )
            success = callback(body)
            logger.info(
                "Thread id: %s Delivery tag: %s Message body: %s Processed...",
                thread_id,
                delivery_tag,
                body,
            )
            cb = functools.partial(self._ack_message, ch, delivery_tag)
            logger.info(f"Sent ack for Delivery tag {delivery_tag}...")
            self.connection.add_callback_threadsafe(cb)
        except:
            logger.log_uncaught_exception()

    def _on_message(self, ch, method_frame, _header_frame, body, args):
        (callback,) = args
        delivery_tag = method_frame.delivery_tag
        t = threading.Thread(
            target=self._do_work, args=(ch, delivery_tag, body, callback)
        )
        t.start()
        self.threads.append(t)

    def consume(self, callback):
        on_message_callback = functools.partial(self._on_message, args=(callback,))
        self.channel.basic_consume(
            queue=self.queue, on_message_callback=on_message_callback
        )
        self.channel.start_consuming()
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Exiting gracefully...")
            self.channel.stop_consuming()
        except:
            logger.log_uncaught_exception()
        finally:
            # Wait for all to complete
            for thread in self.threads:
                thread.join()
            self.connection.close()


class Queue:
    def __init__(self, name, host="rabbitmq"):
        self.name = name
        self.host = host

    def publish(self, message, retry_count=5, retry_interval=10):
        while retry_count > 0:
            try:
                vhost = settings.rabbitmq_vhost
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.host, virtual_host=vhost, credentials=credentials())
                )
                channel = connection.channel()

                channel.queue_declare(queue=self.name, durable=True)

                channel.basic_publish(
                    exchange="",
                    routing_key=self.name,
                    body=json.dumps(message),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    ),
                )

                connection.close()
                break
            except:
                logger.warn(
                    f"Retries left {retry_count - 1} for queue {self.name} and message {str(message)}"
                )
                retry_count -= 1
                if retry_count > 0:
                    time.sleep(retry_interval)
                else:
                    logger.error(
                        f"Retry limit exceeded for queue {self.name} and message {str(message)}"
                    )
                    logger.log_uncaught_exception()

    def consume(self, callback, threaded=False, num_threads=1):
        if threaded:
            ThreadedConsumer(self.name, num_threads, host=self.host).consume(callback)
        else:
            Consumer(self.name, host=self.host).consume(callback)
