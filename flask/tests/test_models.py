import os
from datetime import datetime, timedelta

import pytest

from app import db
from app.models import (
    Person, LoginMethod, OtpMethod, RecoveryCode, get_class_from_string,
)

with open(os.path.join(os.path.dirname(__file__), 'clear_db.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

###
# functions
# #


def test_default_for_dumps():
    pass


def test_get_class_from_string():
    cl = get_class_from_string('Person')
    assert isinstance(cl(), Person)


def test_get_class_from_string_import_error():
    with pytest.raises(ImportError):
        get_class_from_string('NonExistingClass')

###
# VERSIONED MODEL
# #

def test_versioned_model_using_login_method_update_from(
        app,
        client,
        login_method_instance,
        another_login_method_instance
):
    assert login_method_instance.entity_id != another_login_method_instance.entity_id
    assert login_method_instance.version != another_login_method_instance.version
    another_login_method_instance.update_from(login_method_instance)
    assert login_method_instance.entity_id == another_login_method_instance.entity_id
    assert login_method_instance.version == another_login_method_instance.version


def test_versioned_model_using_login_method_get_new_from_scratch(app, client, login_method_instance):
    new_from_scratch = login_method_instance.get_new_from_scratch()
    assert new_from_scratch.active is True
    assert new_from_scratch.previous_version == new_from_scratch.__empty_version__
    assert new_from_scratch.active is True
    assert new_from_scratch.latest is True


def test_versioned_model_using_login_method_get_new_from_existing(app, client, login_method_instance):
    new_from_existing = login_method_instance.get_new_from_existing()
    assert new_from_existing.version != login_method_instance.version
    assert new_from_existing.previous_version == login_method_instance.version
    assert new_from_existing.name == login_method_instance.name
    assert new_from_existing.entity_id == login_method_instance.entity_id


def test_versioned_model_using_login_method_update_previous_records(app, client, mocker, login_method_instance):
    sql = f"""UPDATE {login_method_instance.__tablename__} SET latest = false WHERE entity_id = '{login_method_instance.entity_id}';"""
    with app.app_context():
        connection = db.connect
        with connection.cursor() as cursor:
            spy = mocker.spy(cursor, 'execute')
            login_method_instance.update_previous_records(cursor)
            spy.assert_called_once_with(sql)


def test_versioned_model_using_login_method_is_new(app, client,login_method_instance):
    lm = login_method_instance.get_new_from_scratch()
    assert lm.is_new() is True

###
# LOGIN METHOD
# #


def test_login_method_eq(app, client, login_method_instance):
    lm1 = login_method_instance
    lm2 = login_method_instance
    assert lm1 == lm2


def test_login_method_not_eq(app, client, login_method_instance, another_login_method_instance):
    lm1 = login_method_instance
    lm2 = another_login_method_instance
    assert lm1 != lm2


def test_login_method_update_from(app, client, login_method_instance):
    lm2 = LoginMethod()
    lm2.update_from(login_method_instance)
    assert login_method_instance == lm2


def test_login_method_repr(app, client, login_method_instance):
    assert str(login_method_instance) == '<Login Method test_lm>'


def test_login_method_create_in_database(app, client, mocker, login_method_instance):
    with app.app_context():
        connection = db.connect
        with connection.cursor() as cursor:
            spy = mocker.spy(cursor, 'execute')
            login_method_instance.create_in_database(cursor)
            spy.assert_called_once()

###
# PERSON
# #


def test_person_repr(app, client, user_test_1):
    assert str(user_test_1) == '<Person Ann Black>'


def test_person_create_in_database(app, client, mocker, user_test_1):
    with app.app_context():
        connection = db.connect
        with connection.cursor() as cursor:
            spy = mocker.spy(cursor, 'execute')
            user_test_1.create_in_database(cursor)
            connection.commit()
            spy.assert_called_once()


def test_person_get_name_from_id(app, user_test_1):
    with app.app_context():
        assert user_test_1.get_name_from_id(user_test_1.entity_id) == f"{user_test_1.first_name} {user_test_1.last_name}"


def test_person_get_reset_token():
    pass


def test_person_verify_reset_token():
    pass


def test_person_is_password_valid(user_test_1):
    assert user_test_1.is_password_valid('1234') is True


def test_person_verify_confirmation_token():
    pass


def test_person_is_authenticated_true(app, user_test_1):
    with app.app_context():
        user_test_1.create_token()
        assert user_test_1.is_authenticated is True


def test_person_is_authenticated_false(app, user_test_1):
    with app.app_context():
        assert user_test_1.is_authenticated is False


def test_person_is_active(user_test_1):
    assert user_test_1.is_active is True


def test_person_is_anonymous_true(app, user_test_1):
    with app.app_context():
        assert user_test_1.is_anonymous is True


def test_person_is_anonymous_false(app, user_test_1):
    with app.app_context():
        user_test_1.create_token()
        assert user_test_1.is_anonymous is False


def test_person_get_id(user_test_1):
    entity_id = user_test_1.entity_id
    assert entity_id == user_test_1.get_id()
