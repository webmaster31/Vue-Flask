import logging
import time
from uuid import uuid4

from flask import current_app as app
from itsdangerous import URLSafeTimedSerializer


def generate_confirmation_token(email):
    with app.app_context():
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    with app.app_context():
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            email = serializer.loads(
                token,
                salt=app.config['SECURITY_PASSWORD_SALT'],
                max_age=expiration
            )
        except BaseException as ex:
            logging.error(ex)
            return False
        return email


def generate_access_token(entity_id):
    with app.app_context():
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        current_ux_ts = time.time()
        expires_in = int(current_ux_ts) + int(app.config['ACCESS_TOKEN_EXPIRE'])
        return serializer.dumps(entity_id, salt=app.config['SECURITY_PASSWORD_SALT']), expires_in


def confirm_access_token(token, expiration=None):
    with app.app_context():
        if expiration is None:
            expiration = int(app.config['ACCESS_TOKEN_EXPIRE'])
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            entity_id = serializer.loads(
                token,
                salt=app.config['SECURITY_PASSWORD_SALT'],
                max_age=expiration
            )
        except BaseException as ex:
            logging.error(ex)
            return False
        return entity_id


def generate_recovery_codes(number_of_tokens):
    for _ in range(number_of_tokens):
        yield uuid4().hex.upper()
