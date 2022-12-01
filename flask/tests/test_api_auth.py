from app import create_app


def test_config():
    assert not create_app().testing
    assert create_app(test_config=True).testing


def test_hello_world(client):
    """Start with a blank page."""
    rv = client.get('/')
    assert b'Welcome to Flask Template.' in rv.data


def test_signup(app, client, user_test_1):
    # expecting Content-type: json
    rv = client.post('/signup')
    assert rv.status_code == 400

    user_data = {
        "first_name": "dinara",
        "last_name": "s",
        "email": "dinara@test.c",
        "password": "dinara@test.c"
    }

    # login_method is required
    rv = client.post(
        '/signup',
        json=user_data,
        headers={'Content-Type': 'application/json'}
    )
    json_data = rv.get_json()
    assert 'Invalid login method' in json_data['message']
    assert not json_data['success']

    # signed up successfully
    user_data['login_method'] = "signup"
    rv = client.post(
        '/signup',
        json=user_data,
        headers={'Content-Type': 'application/json'}
    )
    json_data = rv.get_json()
    assert 'User successfully created' in json_data['message']

    # user is created already
    user_data['email'] = "ann.black@mail.c"
    rv = client.post(
        '/signup',
        json=user_data,
        headers={'Content-Type': 'application/json'}
    )
    json_data = rv.get_json()
    assert 'User already exists' in json_data['message']


def test_login(app, client, user_test_1):
    # expecting Content-type: json
    rv = client.post('/login')
    assert rv.status_code == 400

    # email is required
    user_data = {
        "password": user_test_1.raw_password
    }
    rv = client.post(
        '/login',
        json=user_data,
        headers={'Content-Type': 'application/json'}
    )
    json_data = rv.get_json()
    assert 'Email is required.' in json_data['message']
    assert not json_data['success']

    # password is required
    user_data = {
        "email": user_test_1.email
    }
    rv = client.post(
        '/login',
        json=user_data,
        headers={'Content-Type': 'application/json'}
    )
    json_data = rv.get_json()
    assert 'Password is required.' in json_data['message']
    assert not json_data['success']

    # user does not exist
    user_data = {
        "email": f"nonexist{user_test_1.email}",
        "password": user_test_1.raw_password
    }
    rv = client.post(
        '/login',
        json=user_data,
        headers={'Content-Type': 'application/json'}
    )
    json_data = rv.get_json()
    assert 'There is no user with this email.' in json_data['message']
    assert not json_data['success']

    # password is invalid
    user_data = {
        "email": user_test_1.email,
        "password": f"{user_test_1.raw_password}1"
    }
    rv = client.post(
        '/login',
        json=user_data,
        headers={'Content-Type': 'application/json'}
    )
    json_data = rv.get_json()
    assert 'Password is invalid.' in json_data['message']
    assert not json_data['success']

    # login successfully
    user_data = {
        "email": user_test_1.email,
        "password": user_test_1.raw_password
    }
    rv = client.post(
        '/login',
        json=user_data,
        headers={'Content-Type': 'application/json'}
    )
    json_data = rv.get_json()
    assert json_data['success']
    assert user_test_1.email == json_data['user']['email']
    assert 'access_token' in json_data['user']


def test_logout(app, client, user_test_1):
    with client as test_client:
        user_data = {
            "email": user_test_1.email,
            "password": user_test_1.raw_password
        }
        rv = test_client.post(
            '/login',
            json=user_data,
            headers={'Content-Type': 'application/json'}
        )
        json_data = rv.get_json()
        assert 'access_token' in json_data['user']

        rv = test_client.post(
            '/logout',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f"Basic {json_data['user']['access_token']}"
            }
        )
        json_data = rv.get_json()
        assert 'User successfully logged out.' in json_data['message']
        assert json_data['success']


def test_confirm_email(app, client, user_test_1):
    pass


def test_resend_confirmation(app, client, user_test_1, mocker):
    # expecting Content-type: json
    rv = client.post('/resend_confirmation')
    assert rv.status_code == 400

    # email is required
    user_data = {
        "password": user_test_1.raw_password
    }
    rv = client.post(
        '/resend_confirmation',
        json=user_data,
        headers={'Content-Type': 'application/json'}
    )
    json_data = rv.get_json()
    assert 'Email not provided for email verification.' in json_data['message']
    assert not json_data['success']

    # user does not exist
    user_data = {
        "email": f"nonexist{user_test_1.email}"
    }
    rv = client.post(
        '/resend_confirmation',
        json=user_data,
        headers={'Content-Type': 'application/json'}
    )
    json_data = rv.get_json()
    assert 'Couldn\'t find the user with given email address for email verification' in json_data['message']
    assert not json_data['success']

    # resend successfully
    user_data = {
        "email": user_test_1.email
    }
    spy = mocker.patch('app.views.authentication.PersonRepository.send_welcome_email')
    rv = client.post(
        '/resend_confirmation',
        json=user_data,
        headers={'Content-Type': 'application/json'}
    )
    spy.assert_called_once_with(user_test_1)
    json_data = rv.get_json()
    assert json_data['success']
    assert 'A confirmation email has been sent via email.' in json_data['message']


def test_forgot_password(app, client, user_test_1, mocker):
    # expecting Content-type: json
    rv = client.post('/forgot_password')
    assert rv.status_code == 400

    # email is required
    user_data = {
        "password": user_test_1.raw_password
    }
    rv = client.post(
        '/forgot_password',
        json=user_data,
        headers={'Content-Type': 'application/json'}
    )
    json_data = rv.get_json()
    assert 'Email not provided for password reset.' in json_data['message']
    assert not json_data['success']

    # user does not exist
    user_data = {
        "email": f"nonexist{user_test_1.email}"
    }
    rv = client.post(
        '/forgot_password',
        json=user_data,
        headers={'Content-Type': 'application/json'}
    )
    json_data = rv.get_json()
    assert 'Couldn\'t find the user with given email address for email reset' in json_data['message']
    assert not json_data['success']

    # resend successfully
    user_data = {
        "email": user_test_1.email
    }
    spy = mocker.patch('app.views.authentication.PersonRepository.send_reset_password_email')
    rv = client.post(
        '/forgot_password',
        json=user_data,
        headers={'Content-Type': 'application/json'}
    )
    spy.assert_called_once_with(user_test_1)
    json_data = rv.get_json()
    assert json_data['success']
    assert 'Password reset email sent to the user' in json_data['message']


def test_reset_password(app, client, user_test_1):
    pass


def test_change_password(app, client, user_test_1, mocker):
    # login is required
    rv = client.post('/update_password')
    assert rv.status_code == 401

    with client as test_client:
        user_data = {
            "email": user_test_1.email,
            "password": user_test_1.raw_password
        }
        rv = test_client.post(
            '/login',
            json=user_data,
            headers={'Content-Type': 'application/json'}
        )
        json_data = rv.get_json()
        assert 'access_token' in json_data['user']
        access_token = f"Basic {json_data['user']['access_token']}"

        # expecting Content-type: json
        rv = client.post('/update_password')
        assert rv.status_code == 401

        # new password is required
        user_data = {
            "existing_password": user_test_1.raw_password
        }
        rv = client.post(
            '/update_password',
            json=user_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': access_token
            }
        )
        json_data = rv.get_json()
        assert 'Please provide a new password.' in json_data['message']
        assert not json_data['success']

        # existing password is required
        user_data = {
            "new_password": user_test_1.raw_password
        }
        rv = client.post(
            '/update_password',
            json=user_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': access_token
            }
        )
        json_data = rv.get_json()
        assert 'Please provide an existing password.' in json_data['message']
        assert not json_data['success']

        # Existing and new password cannot be same.
        user_data = {
            "existing_password": user_test_1.raw_password,
            "new_password": user_test_1.raw_password
        }
        rv = client.post(
            '/update_password',
            json=user_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': access_token
            }
        )
        json_data = rv.get_json()
        assert 'Existing and new password cannot be same.' in json_data['message']
        assert not json_data['success']

        # Existing password is not valid.
        user_data = {
            "existing_password": f"1user_test_1.raw_password",
            "new_password": user_test_1.raw_password
        }
        rv = client.post(
            '/update_password',
            json=user_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': access_token
            }
        )
        json_data = rv.get_json()
        assert 'Provided existing password is invalid' in json_data['message']
        assert not json_data['success']

        # resend successfully
        user_data = {
            "existing_password": user_test_1.raw_password,
            "new_password": f"1{user_test_1.raw_password}"
        }
        spy = mocker.patch('app.views.authentication.PersonRepository.update')
        rv = client.post(
            '/update_password',
            json=user_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': access_token
            }
        )
        spy.assert_called_once()
        json_data = rv.get_json()
        assert json_data['success']
        assert 'Password has been updated.' in json_data['message']


def test_get_social(app, client, user_test_1):
    pass


def test_delete_social(app, client, user_test_1):
    pass
