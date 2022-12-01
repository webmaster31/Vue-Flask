from app import celery_app
from lib.email_sender import send_custom_email


@celery_app.task(name='send_email')
def send_email(**message):
    result = send_custom_email(message)
    return result.json()
