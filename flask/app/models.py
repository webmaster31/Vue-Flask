import inspect
import json
import logging
import sys
import time
from datetime import datetime, date
from uuid import uuid4, UUID

import jwt
from app import db, pusher_client
from app.tokens import generate_access_token, confirm_access_token, confirm_token, generate_recovery_codes
from app.utils import get_random_string
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash


class ConnectionContext():
    def __init__(self, connection=None):
        self.app_context = None
        self.connection = connection

    def __enter__(self):
        self.app_context = current_app.app_context()
        self.app_context.__enter__()
        if not self.connection:
            self.connection = db.connect
        return self.connection

    def __exit__(self, exc_type, exc_value, tb):
        self.app_context.__exit__(exc_type, exc_value, tb)


def default_for_dumps(o):
    if isinstance(o, (date, datetime)):
        return o.isoformat()


def get_class_from_string(class_name):
    """
    Get a class_name and return the class.
    Raise ImportError if the import failed.
    Raise TypeError if there is no class with the class_name.
    """
    try:
        identifier = getattr(sys.modules[__name__], class_name)
    except ValueError as err:
        raise ImportError("There is no class with the name %s" % class_name) from err
    except AttributeError as err:
        raise ImportError("There is no class with the name %s" % class_name) from err

    if inspect.isclass(identifier):
        return identifier
    raise TypeError("%s is not a class." % class_name)


class VersionedModel:
    """
    An Abstract Model Class that follows insert-only approach.
    Changes to an object result in a new version of that object being stored.
    To accomplish this, every object has 7 base following properties.
    """
    __abstract__ = True
    __empty_version__ = '00000000000000000000000000000000'

    entity_id: str
    version: str
    previous_version: str
    active: bool
    latest: bool
    changed_by_id: str
    changed_on: datetime

    def __init__(self, entity_id=None, version=None, previous_version=None, active=True, latest=True,
                 changed_by_id=None, changed_on=None, **kwargs):
        self.entity_id = entity_id
        self.version = version
        self.previous_version = previous_version
        self.active = active
        self.latest = latest
        self.changed_by_id = changed_by_id
        self.changed_on = changed_on

    def __eq__(self, other):
        raise NotImplementedError

    def create_in_database(self, cursor):
        raise NotImplementedError

    @staticmethod
    def _get_connection(default_connection=None):
        return ConnectionContext(connection=default_connection)

    @staticmethod
    def _notify_object_save(new_entity, table_name, operation):
        from app.tasks import send_task
        send_task('save-notification', 'handle_object_save', new_entity.get_as_dict(), args=[table_name, operation])
        pusher_client.trigger(
            table_name,
            operation,
            new_entity.get_for_api()
        )

    def update_from(self, other):
        if isinstance(other, self.__class__):
            if other.entity_id:
                self.entity_id = other.entity_id
            if other.version:
                self.version = other.version
        else:
            return False

    def get_new_from_scratch(self):
        if not self.entity_id:
            self.generate_entity_id()
        self.version = uuid4().hex
        self.previous_version = self.__empty_version__
        self.active = self.active if self.active is not None else True
        self.latest = True
        return self

    def get_new_from_existing(self):
        properties = self.get_as_dict()
        new_entity = self.__class__(**properties)
        new_entity.version = uuid4().hex
        new_entity.previous_version = self.version
        return new_entity

    def update_previous_records(self, cursor):
        sql = f"""UPDATE {self.__tablename__} SET latest = false WHERE entity_id = '{self.entity_id}';"""
        cursor.execute(sql)

    def save(self, connection=None, commit=True):
        with self._get_connection(default_connection=connection) as connection:
            with connection.cursor() as cursor:
                updated = False
                if self.entity_id and self.version:
                    updated = True
                    new_entity = self.get_new_from_existing()
                    self.update_previous_records(cursor)
                if not self.entity_id or not self.version:
                    new_entity = self.get_new_from_scratch()
                new_entity.create_in_database(cursor)

            if commit:
                connection.commit()
                if cursor:
                    cursor.close()
                operation = 'update' if updated else 'create'
                self._notify_object_save(new_entity, self.__tablename__, operation)
            return new_entity

    @classmethod
    def fetchone_dict(cls, query, commit=True):
        with cls._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                desc = cursor.description
                results = cursor.fetchone()
                if results:
                    results = dict(zip([col[0] for col in desc], results))
            if commit:
                connection.commit()
                if cursor:
                    cursor.close()
            return results

    @classmethod
    def fetchall_dict(cls, query, commit=True):
        with cls._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                desc = cursor.description
                rows = cursor.fetchall()
                results = []
                if rows:
                    for row in rows:
                        results.append(dict(zip([col[0] for col in desc], row)))
            if commit:
                connection.commit()
                if cursor:
                    cursor.close()
            return results

    def get_as_dict(self):
        params = {
            k: val for k, val in self.__dict__.items()
            if not k.startswith('_') and not isinstance(val, VersionedModel)
        }
        for key, val in params.items():
            if isinstance(val, (date, datetime)):
                params[key] = val.isoformat()
        return params

    def get_for_api(self):
        user_data = self.get_as_dict()
        user_data.pop('password', None)
        user_data.pop('raw_password', None)
        user_data.pop('previous_version', None)
        user_data.pop('changed_by_id', None)
        user_data.pop('changed_on', None)
        return user_data

    @classmethod
    def get(cls, value, key='entity_id'):
        query = f"""SELECT * FROM {cls.__tablename__} WHERE {key} = '{str(value)}' AND latest = true AND active = true;"""
        model = cls.fetchone_dict(query)
        if model:
            o = cls()
            for k, v in model.items():
                setattr(o, k, v)
            return o
        return None

    def get_one(self, fields: str, condition: str = ''):
        default_condition = "latest = true AND active = true"
        condition = condition + " AND " + default_condition if condition else default_condition
        query = f"""SELECT {fields} FROM {self.__tablename__} WHERE {condition};"""
        model = self.fetchone_dict(query)
        if model:
            for k, v in model.items():
                setattr(self, k, v)
            return self
        return None

    def get_filtered_all(self, fields: str, value, key='entity_id'):
        """
        Returns filtered entities as list of dicts
        :param fields: fields to select
        :param value: filters select using this value for the key below
        :param key: filters select using this key with the value above
        :return: list of dictionaries or empty list
        """
        query = f"""SELECT {fields} FROM {self.__tablename__} WHERE {key} = '{str(value)}' AND latest = true AND active = true;"""
        return self.fetchall_dict(query)

    def get_all(self, fields: str, condition: str = ''):
        default_condition = "latest = true AND active = true"
        condition = condition + " AND " + default_condition if condition else default_condition
        query = f"""SELECT {fields} FROM {self.__tablename__} WHERE {condition};"""
        return self.fetchall_dict(query)

    def is_new(self):
        return self.previous_version == self.__empty_version__

    def delete(self):
        self.active = False
        self.save()


class UUIDModel(VersionedModel):
    """
    An Abstract Model Class that follows insert-only approach with UUID as ID.
    Changes to an object result in a new version of that object being stored.
    To accomplish this, every object has 7 base following properties.
    """
    __abstract__ = True

    def __eq__(self, other):
        raise NotImplementedError

    def create_in_database(self, cursor):
        raise NotImplementedError

    def generate_entity_id(self):
        self.entity_id = uuid4().hex


class ShortUUIDModel(VersionedModel):
    """
    An Abstract Model Class that follows insert-only approach with short UUID as ID.
    Changes to an object result in a new version of that object being stored.
    To accomplish this, every object has 7 base following properties.
    """
    __abstract__ = True

    def __eq__(self, other):
        raise NotImplementedError

    def create_in_database(self, cursor):
        raise NotImplementedError

    def generate_entity_id(self):
        self.entity_id = get_random_string(10)


class LoginMethod(UUIDModel):
    __tablename__ = 'login_method'

    name: str
    person_id: str
    email: str  # store user email in case it differs from Person
    user_name: str  # store user name in case it differs from Person
    access_token: str
    refresh_token: str
    expires_in: int
    refresh_token_expires_in: int
    sub: str
    scope: str
    token_type: str
    data_access_expiration_time: str

    def __init__(self, name=None, person_id=None, access_token=None,
                 refresh_token=None, expires_in=None, refresh_token_expires_in=None, sub=None,
                 scope=None, token_type=None, email=None, user_name=None,
                 data_access_expiration_time=None, **kwargs):
        self.name = name
        self.person_id = person_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in
        self.refresh_token_expires_in = refresh_token_expires_in
        self.sub = sub
        self.email = email
        self.user_name = user_name
        self.scope = scope
        self.token_type = token_type
        self.data_access_expiration_time = data_access_expiration_time
        super().__init__(**kwargs)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name and \
                   self.person_id == other.person_id and \
                   self.access_token == other.access_token and \
                   self.refresh_token == other.refresh_token and \
                   self.expires_in == other.expires_in and \
                   self.refresh_token_expires_in == other.refresh_token_expires_in and \
                   self.sub == other.sub and \
                   self.email == other.email and \
                   self.user_name == other.user_name and \
                   self.scope == other.scope and \
                   self.token_type == other.token_type and \
                   self.data_access_expiration_time == other.data_access_expiration_time
        else:
            return False

    def update_from(self, other):
        if isinstance(other, self.__class__):
            self.name = other.name
            self.person_id = other.person_id
            self.access_token = other.access_token
            self.refresh_token = other.refresh_token
            self.expires_in = other.expires_in
            self.refresh_token_expires_in = other.refresh_token_expires_in
            self.sub = other.sub
            self.email = other.email
            self.user_name = other.user_name
            self.scope = other.scope
            self.token_type = other.token_type
            self.data_access_expiration_time = other.data_access_expiration_time
            super().update_from(other)
        else:
            return False

    def __repr__(self):
        return '<Login Method {}>'.format(self.name)

    def create_in_database(self, cursor):
        self.changed_by_id = self.person_id if self.is_new() and self.changed_by_id is None else self.changed_by_id
        try:
            # Create a new instance
            sql = "INSERT INTO {} (entity_id, version, previous_version, access_token, refresh_token, expires_in, refresh_token_expires_in, scope, token_type, active, latest, changed_by_id, sub, email, user_name, name, person_id, data_access_expiration_time)" \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
                self.__tablename__)
            cursor.execute(sql, (self.entity_id, self.version, self.previous_version,
                                 self.access_token, self.refresh_token, self.expires_in,
                                 self.refresh_token_expires_in, self.scope, self.token_type,
                                 self.active, self.latest, self.changed_by_id,
                                 self.sub, self.email, self.user_name,
                                 self.name, self.person_id, self.data_access_expiration_time))
        except Exception as e:
            print("Error in SQL:\n", e)


class OtpMethod(UUIDModel):
    __tablename__ = 'otp_method'

    secret: str
    person_id: str
    name: str
    enabled: bool

    def __init__(self, secret=None, person_id=None, name=None, enabled=False, **kwargs):
        self.secret = secret
        self.person_id = person_id
        self.name = name
        self.enabled = enabled
        super().__init__(**kwargs)

    def __repr__(self):
        return '<OTP Method {}>'.format(self.secret)

    def create_in_database(self, cursor):
        self.changed_by_id = self.person_id if self.is_new() and self.changed_by_id is None else self.changed_by_id
        try:
            # Create a new instance
            sql = "INSERT INTO {} (entity_id, version, previous_version, active, latest, changed_by_id, secret, person_id, name, enabled)" \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(self.__tablename__)
            cursor.execute(sql, (self.entity_id, self.version,
                                 self.previous_version, self.active, self.latest, self.changed_by_id,
                                 self.secret, self.person_id, self.name, self.enabled))
        except Exception as e:
            logging.error(f"Error in SQL:\n {e}")

        if self.enabled:
            for code in generate_recovery_codes(RecoveryCode().__number_of_tokens__):
                RecoveryCode(otp_method_id=self.entity_id, token=code).save()
        if not self.enabled:
            for code in RecoveryCode().get_all('*', condition=f"otp_method_id = '{str(self.entity_id)}'"):
                RecoveryCode().get(code.get('entity_id'), key='entity_id').delete()


class Person(UUIDModel):
    __tablename__ = 'person'

    first_name: str
    last_name: str
    email: str
    password: str
    raw_password: str
    login_method: LoginMethod
    verified: bool
    verified_on: int
    access_token: str
    expires_in: int

    # JOINed fields
    latest_clickwrap_accepted: bool

    def __init__(self, first_name=None, last_name=None, email=None, raw_password=None, password=None, verified=False,
                 verified_on=None, access_token=None, expires_in=None,
                 login_method: dict = None, **kwargs):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.raw_password = raw_password
        self.password = generate_password_hash(raw_password) if self.raw_password else password
        self.verified = verified
        self.verified_on = verified_on
        self.access_token = access_token
        self.expires_in = expires_in

        self.login_method = LoginMethod(**login_method) if login_method else None
        super().__init__(**kwargs)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.first_name == other.first_name and \
                   self.last_name == other.last_name and \
                   self.email == other.email and \
                   self.password == other.password and \
                   self.verified == other.verified and \
                   self.verified_on == other.verified_on
        else:
            return False

    def __repr__(self):
        return '<Person {} {}>'.format(self.first_name, self.last_name)

    def create_in_database(self, cursor):
        self.changed_by_id = self.entity_id if self.is_new() and self.changed_by_id is None else self.changed_by_id
        # Create a new instance
        try:
            sql = "INSERT INTO {} (entity_id, version, previous_version, active, latest, changed_by_id, first_name, last_name, email, password, verified, verified_on, access_token, expires_in) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(self.__tablename__)
            cursor.execute(sql, (self.entity_id, self.version, self.previous_version, self.active,
                                 self.latest, self.changed_by_id, self.first_name, self.last_name, self.email,
                                 self.password, self.verified, self.verified_on, self.access_token, self.expires_in))
        except Exception as e:
            logging.warning(f"Error in SQL: {e}")

        if self.login_method:
            self.login_method.person_id = self.entity_id
            self.login_method.save()

    @classmethod
    def get(cls, value, key='entity_id', with_clickwrap_acceptance=False):
        default_condition = f"{cls.__tablename__}.latest = true AND {cls.__tablename__}.active = true"
        condition = f"{cls.__tablename__}.{key} = '{value}'" + " AND " + default_condition
        
        clickwrap_acceptance_query = ""
        if with_clickwrap_acceptance:
            clickwrap_acceptance_query = f""",
            (CASE WHEN EXISTS (SELECT 1 FROM clickwrap_acceptance n WHERE n.user_id = {cls.__tablename__}.entity_id and n.latest=1 and n.active=1 and 
                    (n.clickwrap_content_version, n.clickwrap_version, n.clickwrap_content_md5)=(SELECT content_version, version, content_md5 FROM clickwrap WHERE entity_id="{ClickwrapAgreement.PUBLISHED_UUID}" AND latest=1 AND active=1))
                THEN TRUE ELSE FALSE
            END) as `latest_clickwrap_accepted`
            """

        query = f"""
            SELECT 
                {cls.__tablename__}.*
                {clickwrap_acceptance_query}
            FROM {cls.__tablename__} 
            WHERE {condition};
        """

        model = cls.fetchone_dict(query)
        if model:
            o = cls()
            for k, v in model.items():
                setattr(o, k, v)
            return o
        return None

    def get_name_from_id(self, entity_id):
        person = self.get(entity_id, key='entity_id')
        if person:
            return f"{person.first_name} {person.last_name}"

    def create_token(self):
        self.access_token, self.expires_in = generate_access_token(self.entity_id)

    def get_reset_token(self, expires=3600):
        return jwt.encode(
            {
                'reset_password': self.email,
                'exp': time.time() + expires
            },
            self.password if self.password else self.entity_id,
            algorithm='HS256'
        )

    def verify_reset_token(self, token):
        try:
            email = jwt.decode(
                token,
                self.password if self.password else self.entity_id,
                algorithms=['HS256']
            )['reset_password']
            return self.get(email, key='email')
        except BaseException as ex:
            logging.exception(str(ex))
            return

    def is_password_valid(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def verify_confirmation_token(self, token):
        email = confirm_token(token)
        if email and self.email == email:
            self.verified = True
            self.verified_on = int(time.time())
            return True
        return False

    @property
    def is_authenticated(self):
        """
        This property should return True if the user is authenticated,
        i.e. they have provided valid credentials.
        (Only authenticated users will fulfill the criteria of login_required.)
        :return: boolean
        """
        return confirm_access_token(self.access_token) == self.entity_id

    @property
    def is_active(self):
        """
        This property should return True if this is an active user -
        in addition to being authenticated, they also have activated their account,
        not been suspended, or any condition your application has for rejecting an account.
        Inactive accounts may not log in (without being forced of course).
        :return: boolean
        """
        return self.active

    @property
    def is_anonymous(self):
        """
        This property should return True if this is an anonymous user.
        (Actual users should return False instead.)
        :return: boolean
        """
        return False if self.access_token else True

    def get_id(self):
        """
        This method must return a unicode that uniquely identifies this user,
        and can be used to load the user from the user_loader callback.
        Note that this must be a unicode - if the ID is natively an int or some other type,
        you will need to convert it to unicode.
        :return: entity_id
        """
        return self.entity_id


class RecoveryCode(UUIDModel):
    __tablename__ = 'recovery_code'
    __number_of_tokens__: int = 5

    token: str
    otp_method_id: str

    def __init__(self, token=None, otp_method_id=None, **kwargs):
        self.token = token
        self.otp_method_id = otp_method_id
        super().__init__(**kwargs)

    def __repr__(self):
        return '<Recovery Code {}>'.format(self.token)

    def create_in_database(self, cursor):
        try:
            # Create a new instance
            sql = "INSERT INTO {} (entity_id, version, previous_version, active, latest, changed_by_id, token, otp_method_id)" \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)".format(self.__tablename__)
            cursor.execute(sql, (self.entity_id, self.version,
                                 self.previous_version, self.active, self.latest, self.changed_by_id,
                                 self.token, self.otp_method_id))
        except Exception as e:
            logging.error(f"Error in SQL:\n {e}")

    def verify_recovery_code(self, token, otp_method_id):
        stored_codes = self.get_all('token', condition="otp_method_id = '%s' AND token = '%s'" % (otp_method_id, token))
        if not stored_codes:
            return False
        for code in stored_codes:
            self.get(code.get('token'), key='token').delete()
        return True


class ClickwrapAgreement(UUIDModel):
    __tablename__ = "clickwrap"

    content: str
    content_version: str
    content_md5: str
    status: str  # 'draft' or 'published' or NULL

    # There will always be 2 entities: draft and published; 
    # so the entity IDs are hard-coded so that only these are updated.
    DRAFT_UUID = str(UUID(int=88888888888888)).replace("-", "")
    PUBLISHED_UUID = str(UUID(int=22222222222222)).replace("-", "")

    def __init__(self, content=None, content_version=None, content_md5=None, status=None, **kwargs):
        self.content = content
        self.content_version = content_version
        self.content_md5 = content_md5
        self.status = status
        super().__init__(**kwargs)

    def create_in_database(self, cursor):
        try:
            # Create a new instance
            sql = "INSERT INTO {} (entity_id, version, previous_version, active, latest, changed_by_id, content, content_version, content_md5, status)" \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(self.__tablename__)
            cursor.execute(sql, (self.entity_id, self.version,
                                 self.previous_version, self.active, self.latest, self.changed_by_id,
                                 self.content, self.content_version, self.content_md5, self.status))
        except Exception as e:
            traceback.print_exc()
            logging.error(cursor._last_executed)
            logging.error(f"Error in SQL:\n {e}")

    @classmethod
    def get_all(cls, fields: str, condition: str = 'true', limit: int = None, offset: int = None):
        limit_query = f"LIMIT {limit}" if limit else ""
        offset_query = f"OFFSET {offset}" if offset else ""
        query = f"""SELECT {fields} FROM {cls.__tablename__} WHERE {condition} {limit_query} {offset_query};"""
        models = cls.fetchall_dict(query)
        o = cls()
        for model in models:
            if model:
                for k, v in model.items():
                    setattr(o, k, v)
                yield o

    @classmethod
    def get_content_version_published(cls, content_version, version=None, content_md5=None):
        query = f"""
                SELECT *
                    FROM {cls.__tablename__} 
                    WHERE content_version="{content_version}" 
                    AND entity_id="{cls.PUBLISHED_UUID}"
                    {f' AND version="{version}"' if version else ''}
                    {f' AND content_md5="{content_md5}"' if content_md5 else ''}
                ;"""
        model = cls.fetchone_dict(query)
        if model:
            o = cls()
            for k, v in model.items():
                setattr(o, k, v)
            return o


class ClickwrapAcceptance(UUIDModel):
    __tablename__ = "clickwrap_acceptance"

    ip_address: str
    timestamp: str
    user_id: str
    clickwrap_version: str
    clickwrap_content_version: str
    clickwrap_content_md5: str

    def __init__(self, ip_address=None, user_id=None, clickwrap_version=None, clickwrap_content_version=None,
                 clickwrap_content_md5=None, **kwargs):
        self.ip_address = ip_address
        self.user_id = user_id
        self.clickwrap_version = clickwrap_version
        self.clickwrap_content_version = clickwrap_content_version
        self.clickwrap_content_md5 = clickwrap_content_md5
        super().__init__(**kwargs)

    def create_in_database(self, cursor):
        try:
            # Create a new instance
            sql = "INSERT INTO {} (entity_id, version, previous_version," \
                  "active, latest, changed_by_id, ip_address, user_id, clickwrap_version, clickwrap_content_version, clickwrap_content_md5)" \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(self.__tablename__)
            cursor.execute(sql, (self.entity_id, self.version,
                                 self.previous_version, self.active, self.latest, self.changed_by_id,
                                 self.ip_address, self.user_id, self.clickwrap_version, self.clickwrap_content_version,
                                 self.clickwrap_content_md5
                                 ))
        except Exception as e:
            logging.error(cursor._last_executed)
            logging.error(f"Error in SQL:\n {e}")

    @classmethod
    def has_user_accepted(cls, user_id, content_version, entity_version, content_md5):
        query = f"""
                SELECT COUNT(*) AS accepted 
                    FROM {cls.__tablename__} 
                    WHERE clickwrap_content_version="{content_version}" 
                    AND user_id="{user_id}" 
                    AND clickwrap_content_md5="{content_md5}" 
                    AND clickwrap_version="{entity_version}";
                ;"""
        return cls.fetchone_dict(query)['accepted'] > 0
