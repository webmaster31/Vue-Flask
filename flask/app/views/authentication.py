import base64
from io import BytesIO

import pyotp
import qrcode
import requests
from app.models import Person, OtpMethod, LoginMethod
from app.repositories import PersonRepository, OtpMethodRepository, RepositoryException
from app.utils import urlsafe_base64_decode, force_str
from flask import current_app as app
from flask import request, json, Blueprint
from flask_login import current_user, login_required, logout_user
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

auth = Blueprint('auth', __name__)


@auth.route('/signup', methods=['POST'])
def signup():
    if not request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please use \'application/json\'')),
            status=400,
            mimetype=app.config['MIME_TYPE']
        )

    # if there is login_method in the data then create a person and a method
    if "login_method" not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Invalid login method')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )

    try:
        method_name = request.json['login_method']
        email = request.json['email']
    except KeyError as e:
        return app.response_class(
            response=json.dumps(dict(success=False, message=f'Missing required field: {e.args[0]}')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    first_name = request.json['first_name'] if "first_name" in request.json else None
    last_name = request.json['last_name'] if "last_name" in request.json else None
    password = request.json['password'] if "password" in request.json else None

    person = Person(
        email=email,
        first_name=first_name,
        last_name=last_name,
        raw_password=password,
        login_method={'name': method_name}
    )
    with PersonRepository() as repo:
        if repo.is_exist(person):
            return app.response_class(
                response=json.dumps(dict(success=False, message='User already exists.')),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        repo.save(person)
        return app.response_class(
            response=json.dumps(
                dict(
                    success=True,
                    message='User successfully created and a confirmation email has been sent via email.'
                )
            ),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )


@auth.route('/verify/<token>/<uidb64>', methods=['POST'])
def confirm_email(token, uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
    except UnicodeDecodeError:
        uid = None

    with PersonRepository() as repo:
        user = repo.get_by_id(uid, with_clickwrap_acceptance=True)
        if not user:
            return app.response_class(
                response=json.dumps(dict(success=False, message='User not found')),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        if user.verified:
            return app.response_class(
                response=json.dumps(dict(success=True, message='Account already confirmed. Please login.')),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        if user.verify_confirmation_token(token):
            repo.update(user)
            user = repo.get_by_id(user.entity_id)
            data = repo.login(user)
            return app.response_class(
                response=json.dumps(
                    dict(success=True, message='You have confirmed your account. Thanks!', user=data)
                ),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        return app.response_class(
            response=json.dumps(
                dict(success=False, message='The confirmation link is invalid or has expired.', email=user.email)
            ),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )


@auth.route('/resend_confirmation', methods=['POST'])
def resend_confirmation():
    if not request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please use \'application/json\'')),
            status=400,
            mimetype=app.config['MIME_TYPE']
        )
    if 'email' not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Email not provided for email verification.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )

    with PersonRepository() as repo:
        person = repo.get_by_email(request.json['email'])
        if person:
            repo.send_welcome_email(person)
            return app.response_class(
                response=json.dumps(
                    dict(
                        success=True,
                        message='A confirmation email has been sent via email.'
                    )
                ),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        return app.response_class(
            response=json.dumps(
                dict(
                    success=False,
                    message='Couldn\'t find the user with given email address for email verification'
                )
            ),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )


@auth.route('/forgot_password', methods=['POST'])
def forgot_password():
    if not request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please use \'application/json\'')),
            status=400,
            mimetype=app.config['MIME_TYPE']
        )

    if 'email' not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Email not provided for password reset.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )

    with PersonRepository() as repo:
        person = repo.get_by_email(request.json['email'])
        if person:
            repo.send_reset_password_email(person)
            return app.response_class(
                response=json.dumps(dict(success=True, message='Password reset email sent to the user')),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        return app.response_class(
            response=json.dumps(
                dict(success=False, message='Couldn\'t find the user with given email address for email reset')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )


@auth.route('/reset_password/<token>/<uidb64>', methods=['POST'])
def reset_password(token, uidb64):
    if not request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please use \'application/json\'')),
            status=400,
            mimetype=app.config['MIME_TYPE']
        )
    if 'password' not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Password is not provided for reset.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
    except UnicodeDecodeError:
        uid = None

    with PersonRepository() as repo:
        person = repo.get_by_id(uid)
        if not person:
            return app.response_class(
                response=json.dumps(dict(success=False, message='User not found')),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        if not person.verify_reset_token(token):
            return app.response_class(
                response=json.dumps(dict(success=False, message='Reset Password token has expired')),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        password = request.json['password']
        person.password = None
        person.raw_password = password
        person.changed_on = None
        repo.update(person)
        return app.response_class(
            response=json.dumps(
                dict(success=True, message='Your password has been updated! You are now able to log in.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )


@auth.route('/update_password', methods=['POST'])
@login_required
def change_password():
    if not request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please use \'application/json\'')),
            status=400,
            mimetype=app.config['MIME_TYPE']
        )
    if 'new_password' not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please provide a new password.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )

    if 'existing_password' not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please provide an existing password.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    new_password = request.json['new_password']
    existing_password = request.json['existing_password']
    if new_password == existing_password:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Existing and new password cannot be same.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    with PersonRepository() as repo:
        person = repo.get_by_id(current_user.entity_id)
        if not person.is_password_valid(existing_password):
            return app.response_class(
                response=json.dumps(dict(success=False, message='Provided existing password is invalid')),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        person.password = None
        person.raw_password = new_password
        person.changed_on = None
        repo.update(person)
        return app.response_class(
            response=json.dumps(
                dict(success=True, message='Password has been updated.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )


@auth.route('/qrcode', methods=['POST'])
@login_required
def generate_qr_code():
    if not request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please use \'application/json\'')),
            status=400,
            mimetype=app.config['MIME_TYPE']
        )
    if 'login_type' not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='LoginType not provided for MFA')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    login_type = request.json['login_type']
    email = current_user.email
    if login_type != 'social':
        if 'password' not in request.json:
            return app.response_class(
                response=json.dumps(dict(success=False, message='Password not provided for MFA')),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        with PersonRepository() as p_repo:
            person = p_repo.get_by_email(current_user.email)
            if not person.is_password_valid(request.json['password']):
                return app.response_class(
                    response=json.dumps(dict(success=False, message='Password is invalid.')),
                    status=200,
                    mimetype=app.config['MIME_TYPE']
                )
    otp_method = OtpMethod(person_id=current_user.entity_id)
    with OtpMethodRepository() as repo:
        if not repo.is_exist(otp_method):
            secret = pyotp.random_base32()
            otp_method.secret = secret
            otp_method.person_id = current_user.entity_id
            otp_method.name = 'Authentication App'
            otp_method.enabled = False
            repo.save(otp_method)
        else:
            secret = repo.get_by_person_id(current_user.entity_id).secret
        uri = pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name='OTP PM')
        pil_img = qrcode.make(uri)
        img_io = BytesIO()
        pil_img.save(img_io, 'PNG')
        img_io.seek(0)
        img_str = base64.b64encode(img_io.getvalue()).decode('ascii')
        return app.response_class(
            response=json.dumps(dict(success=True, image=img_str)),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )


@auth.route('/verify_otp', methods=['POST'])
@login_required
def verify_otp():
    if not request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please use \'application/json\'')),
            status=400,
            mimetype=app.config['MIME_TYPE']
        )

    if 'otp' not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='OTP is required.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    otp_method = OtpMethod(person_id=current_user.entity_id)
    with OtpMethodRepository() as otp_repo:
        if not otp_repo.is_exist(otp_method):
            return app.response_class(
                response=json.dumps(
                    dict(success=False, message='OTP method associated with the person not found.')),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        otp_method = otp_repo.get_by_person_id(current_user.entity_id)
        if not pyotp.TOTP(otp_method.secret).verify(str(request.json['otp'])):
            return app.response_class(
                response=json.dumps(dict(success=False, message='You have supplied an invalid MFA token!')),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        codes = otp_repo.create_recovery_codes(otp_method)
        return app.response_class(
            response=json.dumps(
                dict(success=True, message=f"OTP verified successfully", data=dict(otp_verified=True, codes=codes))),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )


@auth.route('/setup_mfa', methods=['POST'])
@login_required
def setup_mfa():
    if not request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please use \'application/json\'')),
            status=400,
            mimetype=app.config['MIME_TYPE']
        )
    if 'mfa_enabled' not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='MFA need to be enabled.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    is_enabled = bool(request.json['mfa_enabled'])
    if is_enabled and 'otp' not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='OTP is required.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    otp_method = OtpMethod(person_id=current_user.entity_id)
    with OtpMethodRepository() as otp_repo:
        if not otp_repo.is_exist(otp_method):
            return app.response_class(
                response=json.dumps(
                    dict(success=False, message='OTP method associated with the person not found.')),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        otp_method = otp_repo.get_by_person_id(current_user.entity_id)
        if is_enabled:
            if not pyotp.TOTP(otp_method.secret).verify(str(request.json['otp'])):
                return app.response_class(
                    response=json.dumps(dict(success=False, message='You have supplied an invalid MFA token!')),
                    status=200,
                    mimetype=app.config['MIME_TYPE']
                )

            otp_method.enabled = is_enabled
            otp_repo.update(otp_method)
        else:
            otp_repo.delete(otp_method)
        return app.response_class(
            response=json.dumps(
                dict(success=True, message=f"MFA {'enabled' if is_enabled else 'disabled'} successfully")),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )


@auth.route('/recovery_codes', methods=['GET', 'POST'])
@login_required
def get_recovery_codes():
    person_id = current_user.entity_id
    with PersonRepository() as repo:
        person = Person(entity_id=person_id)
        if not repo.is_otp_method_enabled(person):
            return app.response_class(
                response=json.dumps(
                    dict(success=False, message='OTP method is not enabled.')),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )

        with OtpMethodRepository() as otp_repo:
            otp_method = otp_repo.get_by_person_id(person_id)
            if request.method == 'GET':
                codes = otp_repo.get_recovery_codes(otp_method)
                return app.response_class(
                    response=json.dumps(dict(success=True, data=codes)),
                    status=200,
                    mimetype=app.config['MIME_TYPE']
                )
            if request.method == 'POST':
                codes = otp_repo.create_recovery_codes(otp_method)
                return app.response_class(
                    response=json.dumps(dict(success=True, data=codes)),
                    status=200,
                    mimetype=app.config['MIME_TYPE']
                )


@auth.route('/verify_recovery_code', methods=['POST'])
def verify_recovery_code():
    if not request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please use \'application/json\'')),
            status=400,
            mimetype=app.config['MIME_TYPE']
        )

    if 'email' not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Email is required.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )

    if 'recovery_code' not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Recovery code is required.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )

    recovery_code = request.json['recovery_code']
    email = request.json['email']

    with PersonRepository() as repo:
        person = repo.get_by_email(email, with_clickwrap_acceptance=True)
        if not person:
            return app.response_class(
                response=json.dumps(dict(success=False, message='User associated with email not found.')),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        if not repo.is_otp_method_enabled(person):
            return app.response_class(
                response=json.dumps(
                    dict(success=False, message='OTP method is not enabled.')),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        with OtpMethodRepository() as otp_repo:
            otp_method = otp_repo.get_by_person_id(person.entity_id)

            if not otp_repo.verify_recovery_code(recovery_code, otp_method):
                return app.response_class(
                    response=json.dumps(dict(success=False, message='You have supplied an invalid recovery code!')),
                    status=200,
                    mimetype=app.config['MIME_TYPE']
                )
            data = repo.login(person)
            return app.response_class(
                response=json.dumps(
                    dict(success=True, message='The MFA recovery code is valid', user=data)),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )


@auth.route('/login_mfa', methods=['POST'])
def login_mfa():
    if not request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please use \'application/json\'')),
            status=400,
            mimetype=app.config['MIME_TYPE']
        )

    if 'email' not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Email is required.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    if 'otp' not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='OTP is required.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    email = request.json['email']
    with PersonRepository() as repo:
        person = repo.get_by_email(email, with_clickwrap_acceptance=True)
        if not person:
            return app.response_class(
                response=json.dumps(dict(success=False, message='User associated with email not found.')),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        otp_method = OtpMethod(person_id=person.entity_id)
        with OtpMethodRepository() as otp_repo:
            if not otp_repo.is_exist(otp_method):
                return app.response_class(
                    response=json.dumps(
                        dict(success=False, message='OTP method associated with the person not found.')),
                    status=200,
                    mimetype=app.config['MIME_TYPE']
                )
            otp_method = otp_repo.get_by_person_id(person.entity_id)
            otp = str(request.json['otp'])
            if pyotp.TOTP(otp_method.secret).verify(otp):
                data = repo.login(person)
                return app.response_class(
                    response=json.dumps(
                        dict(success=True, message='The TOTP MFA token is valid', user=data)),
                    status=200,
                    mimetype=app.config['MIME_TYPE']
                )
            return app.response_class(
                response=json.dumps(dict(success=False, message='You have supplied an invalid MFA token!')),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )


@auth.route('/login', methods=['POST'])
def login():
    if not request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please use \'application/json\'')),
            status=400,
            mimetype=app.config['MIME_TYPE']
        )
    if 'email' not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Email is required.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    if 'password' not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Password is required.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    email = request.json['email']
    with PersonRepository() as repo:
        person = repo.get_by_email(email, with_clickwrap_acceptance=True)
        if person:
            if person.is_password_valid(request.json['password']):
                if repo.is_otp_method_enabled(person):
                    return app.response_class(
                        response=json.dumps(
                            dict(success=True, user=dict(mfa_enabled=True, email=email, verified=person.verified))
                        ),
                        status=200,
                        mimetype=app.config['MIME_TYPE']
                    )
                data = repo.login(person)
                return app.response_class(
                    response=json.dumps(dict(success=True, user=data)),
                    status=200,
                    mimetype=app.config['MIME_TYPE']
                )
            return app.response_class(
                response=json.dumps(dict(success=False, message='Password is invalid.')),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        return app.response_class(
            response=json.dumps(dict(success=False, message='There is no user with this email.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return app.response_class(
        response=json.dumps(dict(success=True, message='User successfully logged out.')),
        status=200,
        mimetype=app.config['MIME_TYPE']
    )


@auth.route("/social", methods=['GET'])
@login_required
def get_social():
    with PersonRepository() as repo:
        login_methods = repo.get_login_methods(current_user)
        result = []
        for lm in login_methods:
            lm_info = {
                'provider': lm['name'],
                'profile': lm
            }
            result.append(lm_info)

        return app.response_class(
            response=json.dumps(dict(success=True, login_methods=result)),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )


@auth.route("/social/<uuid>", methods=['DELETE'])
@login_required
def delete_social(uuid):
    with PersonRepository() as repo:
        try:
            repo.remove_login_method(current_user, uuid)
        except RepositoryException as e:
            return app.response_class(
                response=json.dumps(dict(success=False, message=e.message)),
                status=400,
                mimetype=app.config['MIME_TYPE']
            )
        return app.response_class(
            response=json.dumps(dict(success=True, message='Login method is deleted')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )


@auth.route("/social/github", methods=['POST'])
def social_github():
    if not request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please use \'application/json\'')),
            status=400,
            mimetype=app.config['MIME_TYPE']
        )
    # if there is code in the data then do auth
    if "code" not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='The \'code\' is not provided.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    response = requests.post(
        app.config['GITHUB_OAUTH_URL'],
        data={
            'client_id': app.config['GITHUB_OAUTH_CLIENT_ID'],
            'client_secret': app.config['GITHUB_OAUTH_CLIENT_SECRET'],
            'code': request.json['code']
        },
        headers={
            'Accept': app.config['MIME_TYPE']
        }
    )
    if response.status_code != requests.codes.ok:
        return app.response_class(
            response=json.dumps(dict(success=False, message=response.text)),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    auth_data = response.json()
    if "access_token" not in auth_data:
        return app.response_class(
            response=json.dumps(dict(success=False, message=auth_data['error_description'])),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )

    response = requests.get(
        app.config['GITHUB_USER_INFO_URL'],
        headers={
            'Authorization': f"token {auth_data['access_token']}"
        }
    )
    user_data = response.json()
    if "email" in user_data and user_data["email"] is None:
        response = requests.get(
            f"{app.config['GITHUB_USER_INFO_URL']}/emails",
            headers={
                'Authorization': f"token {auth_data['access_token']}"
            }
        )
        email_data = response.json()
        for email in email_data:
            if email["primary"] is True:
                user_data["email"] = email["email"]
    with PersonRepository() as repo:
        login_method_dict = {
            'name': 'github',
            'access_token': auth_data['access_token'],
            'token_type': auth_data['token_type'],
            'scope': auth_data['scope'],
            'email': user_data["email"],
            'user_name': user_data["name"]
        }
        # add login method to a logged in user
        if current_user.is_authenticated:
            lm = LoginMethod(person_id=current_user.entity_id, **login_method_dict)
            repo.add_login_method(current_user, lm)
            return app.response_class(
                response=json.dumps(dict(
                    success=True,
                    user=current_user.get_for_api(),
                    auth=login_method_dict
                )),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        else:
            full_name = user_data["name"].split(' ')
            first_name = full_name[0]
            last_name = ''
            if len(full_name) > 1:
                last_name = full_name[1]
            person = Person(
                email=user_data["email"],
                first_name=first_name,
                last_name=last_name,
                login_method=login_method_dict
            )
            # or check if user is exists
            if repo.is_exist(person):
                lm = LoginMethod(**login_method_dict)
                repo.add_login_method(person, lm)
                if repo.is_otp_method_enabled(person):
                    return app.response_class(
                        response=json.dumps(dict(success=True, user=dict(mfa_enabled=True), auth=login_method_dict)),
                        status=200,
                        mimetype=app.config['MIME_TYPE']
                    )
            else:
                # create a person
                person.save()
            #  and login him
            user_data = repo.login(person)
            return app.response_class(
                response=json.dumps(dict(
                    success=True,
                    user=user_data,
                    auth=login_method_dict
                )),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )


@auth.route('/social/linkedin', methods=['POST'])
def social_linkedin():
    if not request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please use \'application/json\'')),
            status=400,
            mimetype=app.config['MIME_TYPE']
        )
    # if there is code in the data then do auth
    if "code" not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='The \'code\' is not provided.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    response = requests.post(
        app.config['LINKEDIN_OAUTH_URL'],
        data={
            'client_id': app.config['LINKEDIN_OAUTH_CLIENT_ID'],
            'client_secret': app.config['LINKEDIN_OAUTH_CLIENT_SECRET'],
            'code': request.json['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': app.config['SOCIAL_AUTH_REDIRECT_URI']
        },
        headers={
            'Accept': app.config['MIME_TYPE']
        }
    )

    auth_data = response.json()
    if "access_token" not in auth_data:
        return app.response_class(
            response=json.dumps(dict(success=False, message=auth_data['error_description'])),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    response = requests.get(
        app.config['LINKEDIN_USER_INFO_URL'],
        headers={
            'Authorization': f"Bearer {auth_data['access_token']}"
        }
    )
    user_data = response.json()

    response = requests.get(
        app.config['LINKEDIN_USER_EMAIL_URL'],
        headers={
            'Authorization': f"Bearer {auth_data['access_token']}"
        }
    )
    email_data = response.json()

    with PersonRepository() as repo:
        user_dict = {
            'first_name': user_data['localizedFirstName'],
            'last_name': user_data['localizedLastName'],
            'email': email_data['elements'][0]['handle~']['emailAddress']
        }
        login_method_dict = {
            'name': 'linkedin',
            'access_token': auth_data['access_token'],
            'expires_in': auth_data['expires_in'],
            'email': user_dict["email"],
            'user_name': f"{user_dict['first_name']} {user_dict['last_name']}"
        }
        # add login method to a logged in user
        if current_user.is_authenticated:
            lm = LoginMethod(person_id=current_user.entity_id, **login_method_dict)
            repo.add_login_method(current_user, lm)
            return app.response_class(
                response=json.dumps(dict(
                    success=True,
                    user=current_user.get_for_api(),
                    auth=login_method_dict
                )),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        else:
            person = Person(**user_dict, login_method=login_method_dict)
            # or check if user is exists
            if repo.is_exist(person):
                lm = LoginMethod(**login_method_dict)
                repo.add_login_method(person, lm)
                if repo.is_otp_method_enabled(person):
                    return app.response_class(
                        response=json.dumps(dict(success=True, user=dict(mfa_enabled=True), auth=login_method_dict)),
                        status=200,
                        mimetype=app.config['MIME_TYPE']
                    )
            else:
                # create a person
                person.save()
            #  and login him
            user_data = repo.login(person)
            return app.response_class(
                response=json.dumps(dict(
                    success=True,
                    user=user_data,
                    auth=login_method_dict
                )),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )


@auth.route("/social/google", methods=['POST'])
def social_google():
    if not request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please use \'application/json\'')),
            status=400,
            mimetype=app.config['MIME_TYPE']
        )
    # if there is code in the data then do auth
    if "idtoken" not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='The \'idtoken\' is not provided.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(
            request.json["idtoken"],
            google_requests.Request(),
            app.config['GOOGLE_OAUTH_CLIENT_ID']
        )
        if idinfo['aud'] == app.config['GOOGLE_OAUTH_CLIENT_ID']:
            # ID token is valid. Get the user's Google Account ID from the decoded token.
            with PersonRepository() as repo:
                user_dict = {
                    'first_name': idinfo['given_name'],
                    'last_name': idinfo['family_name'],
                    'email': idinfo['email'],
                    'verified': idinfo['email_verified']
                }
                login_method_dict = {
                    'name': 'google',
                    'sub': idinfo['sub'],
                    'expires_in': idinfo['exp'],
                    'access_token': request.json["idtoken"],
                    'email': user_dict["email"],
                    'user_name': f"{user_dict['first_name']} {user_dict['last_name']}"
                }
                # add login method to a logged in user
                if current_user.is_authenticated:
                    lm = LoginMethod(person_id=current_user.entity_id, **login_method_dict)
                    repo.add_login_method(current_user, lm)
                    return app.response_class(
                        response=json.dumps(dict(
                            success=True,
                            user=current_user.get_for_api(),
                            auth=login_method_dict
                        )),
                        status=200,
                        mimetype=app.config['MIME_TYPE']
                    )
                else:
                    person = Person(**user_dict, login_method=login_method_dict)
                    # or check if user is exists
                    if repo.is_exist(person):
                        lm = LoginMethod(**login_method_dict)
                        repo.add_login_method(person, lm)
                        if repo.is_otp_method_enabled(person):
                            return app.response_class(
                                response=json.dumps(
                                    dict(success=True, user=dict(mfa_enabled=True), auth=login_method_dict)),
                                status=200,
                                mimetype=app.config['MIME_TYPE']
                            )
                    else:
                        # create a person
                        person.save()
                    #  and login him
                    user_data = repo.login(person)
                    return app.response_class(
                        response=json.dumps(dict(
                            success=True,
                            user=user_data,
                            auth=login_method_dict
                        )),
                        status=200,
                        mimetype=app.config['MIME_TYPE']
                    )
        else:
            raise ValueError
    except ValueError:
        # Invalid token
        return app.response_class(
            response=json.dumps(
                dict(success=False, message='Invalid token.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )


@auth.route("/social/facebook", methods=['POST'])
def social_facebook():
    if not request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='Please use \'application/json\'')),
            status=400,
            mimetype=app.config['MIME_TYPE']
        )
    if "accessToken" not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='The \'accessToken\' is not provided.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    if "data_access_expiration_time" not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='The \'data_access_expiration_time\' is not provided.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    if "expiresIn" not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='The \'expiresIn\' is not provided.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    if "grantedScopes" not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='The \'grantedScopes\' is not provided.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    if "userID" not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='The \'userID\' is not provided.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    if "email" not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='The \'email\' is not provided.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    if "name" not in request.json:
        return app.response_class(
            response=json.dumps(dict(success=False, message='The \'name\' is not provided.')),
            status=200,
            mimetype=app.config['MIME_TYPE']
        )
    with PersonRepository() as repo:
        login_method_dict = {
            'name': 'facebook',
            'access_token': request.json['accessToken'],
            'data_access_expiration_time': request.json['data_access_expiration_time'],
            'expires_in': request.json['expiresIn'],
            'scope': request.json['grantedScopes'],
            'email': request.json['email'],
            'user_name': request.json['name']
        }
        # add login method to a logged in user
        if current_user.is_authenticated:
            lm = LoginMethod(person_id=current_user.entity_id, **login_method_dict)
            repo.add_login_method(current_user, lm)
            return app.response_class(
                response=json.dumps(dict(
                    success=True,
                    user=current_user.get_for_api(),
                    auth=login_method_dict
                )),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )
        else:
            full_name = request.json['name'].split(' ')
            first_name = full_name[0]
            last_name = ''
            if len(full_name) > 1:
                last_name = full_name[1]
            person = Person(
                email=request.json["email"],
                first_name=first_name,
                last_name=last_name,
                login_method=login_method_dict
            )
            # or check if user is exists
            if repo.is_exist(person):
                lm = LoginMethod(**login_method_dict)
                repo.add_login_method(person, lm)
                if repo.is_otp_method_enabled(person):
                    return app.response_class(
                        response=json.dumps(dict(success=True, user=dict(mfa_enabled=True), auth=login_method_dict)),
                        status=200,
                        mimetype=app.config['MIME_TYPE']
                    )
            else:
                # create a person
                person.save()
            #  and login him
            user_data = repo.login(person)
            return app.response_class(
                response=json.dumps(dict(
                    success=True,
                    user=user_data,
                    auth=login_method_dict
                )),
                status=200,
                mimetype=app.config['MIME_TYPE']
            )

