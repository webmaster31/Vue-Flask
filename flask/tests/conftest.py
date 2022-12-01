import os
from datetime import datetime, timedelta

import pytest

from app import create_app, db
from app.models import Person, LoginMethod

with open(os.path.join(os.path.dirname(__file__), 'clear_db.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


def clear_db(app):
    """Clear existing data in tables."""
    with app.app_context():
        with db.connection.cursor() as cursor:
            for sql in _data_sql.split(';\n'):
                if sql:
                    cursor.execute(f"{sql};")
            db.connection.commit()


@pytest.fixture
def app():
    app = create_app(test_config=True)
    yield app
    # clear the DB after tests
    clear_db(app)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def user_test_1(app):
    with app.app_context():
        person = Person(first_name='Ann', last_name='Black', email='ann.black@mail.c', raw_password='1234')
        person.save()
        return person


@pytest.fixture
def user_test_2(app):
    with app.app_context():
        person = Person(first_name='User', last_name='Test2', email='user.test.2@mail.c', raw_password='1234')
        person.save()
        return person


@pytest.fixture
def non_existing_user(app):
    return Person(first_name='Non', last_name='Existing', email='non.existing@mail.c')


@pytest.fixture
def non_active_user(app):
    with app.app_context():
        person = Person(first_name='Non', last_name='Existing', email='not.active@mail.c', active=False)
        person.save()
        return person


@pytest.fixture
def login_method_instance():
    return LoginMethod(
        entity_id='test_entity_id',
        version='test_version',
        previous_version='test_previous_version',
        active=True,
        latest=True,
        changed_by_id='test_changed_by_id',
        changed_on=datetime.now(),
        name='test_lm',
        person_id='test_id',
        access_token='test_token',
        refresh_token='test_refresh_token',
        expires_in=565656,
        refresh_token_expires_in='test_rt_expires_in',
        sub='test_sub',
        scope='test_scope',
        token_type='test_token_type',
        email='test_email',
        user_name='test_username',
        data_access_expiration_time='test_daet'
    )


@pytest.fixture
def another_login_method_instance():
    return LoginMethod(
        entity_id='another_test_entity_id',
        version='another_test_version',
        previous_version='another_test_previous_version',
        active=True,
        latest=True,
        changed_by_id='another_test_changed_by_id',
        changed_on=datetime.now(),
        name='another_test_lm',
        person_id='another_test_id',
        access_token='another_test_token',
        refresh_token='another_test_refresh_token',
        expires_in='another_test_expires_in',
        refresh_token_expires_in='another_test_rt_expires_in',
        sub='another_test_sub',
        scope='another_test_scope',
        token_type='another_test_token_type',
        email='another_test_email',
        user_name='another_test_username',
        data_access_expiration_time='another_test_daet'
    )
