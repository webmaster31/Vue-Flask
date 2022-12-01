import json
import hashlib

from app.models import Person, LoginMethod, OtpMethod, VersionedModel, RecoveryCode, ClickwrapAcceptance, ClickwrapAgreement
from app.tasks import send_task, send_message
from app.tokens import generate_confirmation_token, generate_recovery_codes
from app.utils import urlsafe_base64_encode, force_bytes
from flask import current_app
from flask_login import login_user


class RepositoryException(Exception):
    def __init__(self, message, *errors):
        Exception.__init__(self, message)
        self.message = message
        self.errors = errors


class Repository:
    """
    Base Repository class.
    The repository exposes a consistent API that exchanges data in terms of objects
    without any of the underlying operations being exposed to the code using it.
    """

    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        # can test for type and handle different situations
        self.close()

    def complete(self):
        pass

    def close(self):
        pass

    @staticmethod
    def get_by_id(uuid: str) -> VersionedModel:
        """Method gets string uuid and returns a VersionedModel object"""
        raise NotImplementedError

    @staticmethod
    def is_exist(o: VersionedModel):
        raise NotImplementedError

    @staticmethod
    def update(o: VersionedModel):
        """Method gets VersionedModel object and call o.save()"""
        o.save()

    @staticmethod
    def delete(o: VersionedModel):
        """Method gets VersionedModel object and call o.delete()"""
        o.delete()

    @staticmethod
    def save(o: VersionedModel):
        raise NotImplementedError

    @staticmethod
    def create(o: VersionedModel):
        o.save()
        return o.get_for_api()


class PersonRepository(Repository):
    """
    Person Repository class.
    The repository exposes a consistent API that exchanges data in terms of objects
    without any of the underlying operations being exposed to the code using it.
    """

    def add_login_method(self, person: Person, login_method: LoginMethod):
        if person.entity_id is not None:
            person_login_method = self.get_login_method(person, login_method)
            if person_login_method and person_login_method != login_method:
                person_login_method.update_from(login_method)
                person_login_method.person_id = person.entity_id
                person_login_method.changed_by_id = person.entity_id
                person_login_method.save()
            elif person_login_method is None:
                login_method.person_id = person.entity_id
                login_method.changed_by_id = person.entity_id
                login_method.save()
            return
        raise RepositoryException(message='Person should have entity_id')

    @staticmethod
    def get_by_id(uuid: str, **kwargs) -> Person:
        """Method accepts entity_id and returns Person object"""
        return Person().get(uuid, key='entity_id', **kwargs)

    @staticmethod
    def get_by_email(email: str, **kwargs) -> Person:
        """Method accepts email and returns Person object"""
        return Person().get(email, key='email', **kwargs)

    @staticmethod
    def get_login_method(person: Person, login_method: LoginMethod):
        """
        Get existing person's login method based on name or entity_id
        :param person:
        :param login_method:
        :return: LoginMethod or None
        """
        login_methods = LoginMethod().get_filtered_all(
            '*',
            person.entity_id,
            key='person_id'
        )
        for lm in login_methods:
            if lm['name'] == login_method.name or lm['entity_id'] == login_method.entity_id:
                return LoginMethod(**lm)
        return None

    @staticmethod
    def get_login_methods(person: Person):
        """
        Returns person's login methods as list of dicts
        :param person: Person for whom gets login methods
        :return: list of dictionaries or empty list
        """
        login_methods = LoginMethod().get_filtered_all(
            'access_token, entity_id, expires_in, name, refresh_token, refresh_token_expires_in, scope, token_type, user_name, email',
            person.entity_id,
            key='person_id'
        )
        return login_methods

    @staticmethod
    def is_exist(person: Person):
        p = None
        if person.email:
            p = person.get(person.email, key='email')
        elif person.entity_id:
            p = person.get(person.entity_id, key='entity_id')
        return True if p else False

    def login(self, person: Person):
        """
        The method logins person and returns a dict adapted to API
        :param person: Person
        :return: dict
        """
        person.create_token()
        person.save()
        login_user(person)
        data = person.get_for_api()
        data.update({'mfa_enabled': self.is_otp_method_enabled(person)})
        return data

    @staticmethod
    def remove_login_method(person: Person, entity_id: str):
        """
        Removes person's login method
        :param person: Person
        :param entity_id: id of the login method
        :raise: RepositoryException if login method with id doesn't exists
        """
        lm = LoginMethod().get(entity_id, key='entity_id')
        if lm and lm.person_id == person.entity_id:
            lm.delete()
        else:
            raise RepositoryException(message=f'This user doesn\'t have login method {entity_id}')

    @staticmethod
    def is_otp_method_enabled(person: Person):
        otp_method = OtpMethod().get(person.entity_id, key='person_id')
        return bool(otp_method and otp_method.enabled)

    def save(self, person: Person):
        person.save()  # TODO: Switch to async save.
        self.send_welcome_email(person)

    def send_welcome_email(self, person: Person):
        person = self.get_by_email(person.email)
        token = generate_confirmation_token(person.email)
        uid = urlsafe_base64_encode(force_bytes(person.entity_id))
        confirmation_link = current_app.config.get('FRONTEND_URL') + '/session/login/' + token + '/' + uid
        send_message('email-transmitter', {
            "event": "USER_CREATED",
            "data": {"recipient_name": f"{person.first_name} {person.last_name}", "confirmation_link": confirmation_link},
            "to_emails": [person.email]
        })

    def send_reset_password_email(self, person: Person):
        person = self.get_by_email(person.email)
        token = person.get_reset_token()
        uid = urlsafe_base64_encode(force_bytes(person.entity_id))
        password_reset_url = current_app.config.get('FRONTEND_URL') + '/session/reset-password/' + token + '/' + uid
        send_message('email-transmitter', {
            "event": "RESET_PASSWORD",
            "data": {"recipient_name": f"{person.first_name} {person.last_name}", "password_reset_url": password_reset_url},
            "to_emails": [person.email]
        })


class OtpMethodRepository(Repository):

    @staticmethod
    def get_by_id(uuid: str) -> OtpMethod:
        return OtpMethod().get(uuid, key='entity_id')

    @staticmethod
    def get_by_person_id(person_id: str):
        return OtpMethod().get(person_id, key='person_id')

    @staticmethod
    def is_exist(otp_method: OtpMethod):
        method = None
        if otp_method.person_id:
            method = otp_method.get(otp_method.person_id, key='person_id')
        return True if method else False

    @staticmethod
    def save(otp_method: OtpMethod):
        otp_method.save()  # TODO: Switch to async save.

    @staticmethod
    def get_recovery_codes(otp_method: OtpMethod):
        data = RecoveryCode().get_filtered_all(
            'token',
            otp_method.entity_id,
            key='otp_method_id'
        )
        return list({code.get('token') for code in data})

    def create_recovery_codes(self, otp_method: OtpMethod):
        all_tokens = []
        self.delete_recovery_codes(otp_method)
        for code in generate_recovery_codes(RecoveryCode().__number_of_tokens__):
            RecoveryCode(otp_method_id=otp_method.entity_id, token=code).save()
            all_tokens.append(code)
        return all_tokens

    @staticmethod
    def delete_recovery_codes(otp_method: OtpMethod):
        for code in RecoveryCode().get_all('*', condition=f"otp_method_id = '{str(otp_method.entity_id)}'"):
            RecoveryCode().get(code.get('entity_id'), key='entity_id').delete()

    @staticmethod
    def verify_recovery_code(code, otp_method: OtpMethod):
        try:
            return RecoveryCode().verify_recovery_code(code, otp_method.entity_id)
        except Exception as ex:
            raise RepositoryException(ex)


class ClickwrapRepository(Repository):

    @staticmethod
    def get_by_id(uuid: str) -> ClickwrapAgreement:
        return ClickwrapAgreement.get(uuid, key='entity_id')

    def get_draft(self):
        return ClickwrapAgreement.get(ClickwrapAgreement.DRAFT_UUID, 'entity_id')

    def get_or_create_draft(self):
        return self.get_draft() or ClickwrapAgreement(entity_id=ClickwrapAgreement.DRAFT_UUID)

    def get_published(self):
        return ClickwrapAgreement.get(ClickwrapAgreement.PUBLISHED_UUID, 'entity_id')

    def get_or_create_published(self):
        return self.get_published() or ClickwrapAgreement(entity_id=ClickwrapAgreement.PUBLISHED_UUID)

    def save_draft(self, content: str, content_version: str):
        clickwrap = self.get_or_create_draft()
        clickwrap.entity_id = ClickwrapAgreement.DRAFT_UUID
        clickwrap.content = content
        clickwrap.content_version = content_version
        content_in_bytes = clickwrap.content.encode()
        clickwrap.content_md5 = hashlib.md5(content_in_bytes).hexdigest()
        clickwrap.status = "draft"
        clickwrap.save()  # TODO: Switch to async save
        return clickwrap

    def publish(self, content, content_version):
        self.save_draft(content, content_version)

        clickwrap = self.get_or_create_published()
        clickwrap.entity_id = ClickwrapAgreement.PUBLISHED_UUID
        clickwrap.content = content
        clickwrap.content_version = content_version
        content_in_bytes = clickwrap.content.encode()
        clickwrap.content_md5 = hashlib.md5(content_in_bytes).hexdigest()
        clickwrap.status = "published"
        clickwrap.save()  # TODO: Switch to async save
        return clickwrap

    def get_content_version_published(self, content_version, version=None, content_md5=None):
        return ClickwrapAgreement.get_content_version_published(
            content_version,
            version=version,
            content_md5=content_md5
        )

    def accept_clickwrap(self, acceptance: ClickwrapAcceptance):
        acceptance = acceptance.save()
        return acceptance

    def has_user_accepted(self, acceptance: ClickwrapAcceptance):
        return ClickwrapAcceptance.has_user_accepted(
            acceptance.user_id,
            acceptance.clickwrap_content_version,
            acceptance.clickwrap_version,
            acceptance.clickwrap_content_md5
        )
