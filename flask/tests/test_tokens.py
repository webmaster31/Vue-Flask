import time
from unittest.mock import ANY

from itsdangerous import URLSafeTimedSerializer

from app.tokens import (
    generate_access_token, generate_confirmation_token, confirm_token,
    confirm_access_token,
)


def test_generate_access_token(app, mocker, user_test_1):
    with app.app_context():
        spy = mocker.spy(URLSafeTimedSerializer, 'dumps')
        generate_access_token(user_test_1.entity_id)
        assert spy.call_count == 1
        spy.assert_called_once_with(ANY, user_test_1.entity_id, salt=app.config['SECURITY_PASSWORD_SALT'])


def test_confirm_access_token(app, user_test_1):
    with app.app_context():
        token, _ = generate_access_token(user_test_1.entity_id)

        entity_id = confirm_access_token(token)
        assert entity_id is not False
        assert entity_id == user_test_1.entity_id

        time.sleep(2)

        entity_id = confirm_access_token(token, expiration=1)
        assert entity_id is False


def test_generate_confirmation_token(app, mocker, user_test_1):
    with app.app_context():
        spy = mocker.spy(URLSafeTimedSerializer, 'dumps')
        generate_confirmation_token(user_test_1.email)
        assert spy.call_count == 1
        spy.assert_called_once_with(ANY, user_test_1.email, salt=app.config['SECURITY_PASSWORD_SALT'])


def test_confirm_token(app, user_test_1):
    with app.app_context():
        token = generate_confirmation_token(user_test_1.email)

        email = confirm_token(token)
        assert email is not False
        assert email == user_test_1.email

        time.sleep(2)

        email = confirm_token(token, expiration=1)
        assert email is False
