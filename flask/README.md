# Flask Template
The Flask API Template

## Install

<details>
  <summary><b>Click here to read how to install project</b></summary>

1. Install the project near the `services` like this:<br>
.<br>
├── flask<br>
├── services
<br><br>
2. Copy `.env.dev` and rename it to `.env`
<br><br>
3. Set the empty variables in `.env` as described in [the description of Env variables](#env-variables) section.
<br><br>
4. Start the docker services from `services`. You can see the logs of API running `docker-compose logs api` from `services` folder.
<br><br>
5. Go to [localhost:5000](http://localhost:5000/). On success you'll see there `Welcome to Flask Template.`
</details>


## Env Variables
<details>
  <summary><b>Click here to see the env variables used</b></summary>

#### All settings are set to default values.
If you want to change any settings manually please use the variable hints:
1. Flask Configs
   ```dotenv
   FLASK_ENV=development # only either be development, production or test
   SECRET_KEY=puthereyoursecretkey # flask app secret key
   SECURITY_PASSWORD_SALT=puthereyoursecretpasswordsalt
   ACCESS_TOKEN_EXPIRE=3600 # logged in user's access token validity time in seconds
   ```
2. MySQL Configs
   
   These parameters should be same in both `.env` files here and in `services`.
   ```dotenv
   MYSQL_HOST=mysql
   MYSQL_USER=flask_mysql_user
   MYSQL_PASSWORD=flask_mysql_pass
   MYSQL_PORT=3306
   MYSQL_DATABASE=flask_mysql
   MYSQL_TEST_PORT=3307
   MYSQL_TEST_HOST=mysql_test
   MYSQL_TEST_DATABASE=test_core
   ```
3. RabbitMQ Configs
   
   These parameters should be the same in both `.env` files here and in `services`.
   ```dotenv
   RABBITMQ_USER=rabbituser
   RABBITMQ_PASSWORD=rabbituserpass
   RABBITMQ_VHOST=rabbitmq_template_host
   BROKER_PATH=rabbitmq:5672
   MQ_EXCHANGE=rabbitmq_exchange
   ```
4. Social Oauth Configs
   
   To be able to sign in using social oauth please create apps as described in `services` and set the following variables in `.env`
   ```dotenv
   GITHUB_CLIENT_ID=
   GITHUB_OAUTH_CLIENT_SECRET=
   LINKEDIN_CLIENT_ID=
   LINKEDIN_OAUTH_CLIENT_SECRET=
   GOOGLE_CLIENT_ID=
   ```
5. Rollbar Configs
   
   To enable logging go to [rollbar](https://rollbar.com/) and register a free account. During the setup Rollbar asks for programming language. Choose any you like and copy from the code `access_token`.
<br><br>Another way to retrieve `access_token` is to create a Project, then go to the Projects menu -> Project Access Tokens and copy the one called `post_server_item`.
   ```dotenv
   ROLLBAR_ACCESS_TOKEN= # token copied from step described above
   ```
<br>
6. Pusher Configs

Create an account and get the keys as described in [instruction](https://pusher.com/docs/) (Channels -> Getting Started).
Fill the following .env variables:
   ``` dotenv
   PUSHER_APP_ID=
   PUSHER_API_KEY=
   PUSHER_API_SECRET=
   PUSHER_CLUSTER=
   ```

The .env variables `PUSHER_APP_ID` and `PUSHER_CLUSTER` should match the same variables from [reachable-moment-vue](https://github.com/EcorRouge/reachable-moment-vue) repository. 

**How to use pusher channels and events:**
![Pusher API message example](https://user-images.githubusercontent.com/5466965/153798486-d3ffcd19-38c8-4f0b-a8ed-32da48944e2b.png)
   
The Channel is the lowercase name of entity that was changes. The channels that are used:
* person
* login_method
* otp_method
* recovery_code
* schedule
* event (Reachable Moment instance, not Pusher event)

The Event shows the action that happened with the Channel. It can be created (`create`) and updated (`update`).

</details>


## API endpoints
All the endpoints accepts header `Content-type: 'application/json'`

Server accepts header `Authorization: Basic put-the-access-token-here`. How to get access token? See [login](#login)

### Authorization API

<details>
  <summary><b>Click here to open API docs</b></summary>

### /login
Accepts **POST**. Requires body:
```json
{
    "email": "email",
    "password": "password"
}
```
Returns in case of success:
```json
{
    "success": true,
    "user": {
        "access_token": "IjE0ZDQyODZjMmVlMjQ2NTk5M2I2NWMwYzhkZmYyZWQ0Ig.Ya9VVg.Nb1lCZ9yFhjARI9Ht6dzvNRBW2k",
        "active": 1,
        "email": "oftomorrow@gmail.com",
        "entity_id": "14d4286c2ee2465993b65c0c8dff2ed4",
        "first_name": "dinara",
        "last_name": "s",
        "latest": 1,
        "login_method": null,
        "verified": 0,
        "verified_on": null,
        "mfa_enabled": false,
        "expires_in": 1640629460
    }
}
```

### /logout
**Login is required.**
Accepts **POST**. 
Returns in case of success:
```json
{
    "success": true,
    "message": "User successfully logged out."
}
```

### /signup
Accepts **POST**. Requires body:

```json
{
    "login_method": "signup",
    "first_name": "dinara",
    "last_name": "s",
    "email": "email",
    "password": "password"
}
```
`login_method` might be a name of social network or `signup` if user sign up using email and password.

Returns in case of success:
```json
{
    "message": "User successfully created and a confirmation email has been sent via email.",
    "success": true
}
```

### /verify/{token}/{uidb64}
Accepts **POST**.

`token` and `uidb64` are sent in signup email

Returns in case of success:
```json
{
  "success": true, 
  "message": "You have confirmed your account. Thanks!",
  "user": {
        "access_token": "AccessToken",
        "active": 1,
        "email": "test@test.com",
        "entity_id": "",
        "first_name": "Deepak",
        "last_name": "Paudel",
        "latest": 1,
        "login_method": null,
        "verified": 1,
        "verified_on": 1638982653,
        "mfa_enabled": false,
        "expires_in": 1640629460
  }
}
```

### /resend_confirmation
Accepts **POST**. Requires body:

```json
{
    "email": "email"
}
```

Returns in case of success:
```json
{
    "message": "A confirmation email has been sent via email.",
    "success": true
}
```

### /forgot_password
Accepts **POST**. Requires body:

```json
{
    "email": "email"
}
```

Returns in case of success:
```json
{
    "message": "Password reset email sent to the user",
    "success": true
}
```

### /reset_password/{token}/{uidb64}
Accepts **POST**. Requires body:

`token` and `uidb64` are sent in forgot password email

```json
{
    "password": "password"
}
```

Returns in case of success:
```json
{
    "message": "Your password has been updated! You are now able to log in.",
    "success": true
}
```

### /update_password
Accepts **POST**. Requires body:

```json
{
    "existing_password": "password",
    "new_password": "my_new_password"
}
```

Returns in case of success:
```json
{
    "message": "Password has been updated!!",
    "success": true
}
```


### /qrcode
Accepts **POST**. Requires body:

```json
{
    "password": "password",
    "login_type": "signup"
}
```
The **login_type** can be **signup** or **social**. For **social** login, we don't need to provide **password**.

Returns image in byte format in case of success

### /verify_otp
Accepts **POST**. Requires body:

```json
{
    "otp": 123456
}
```
Returns in case of success:
```json
{
    "message": "OTP verified successfully",
    "success": true,
    "data": {
       "otp_verified": true, 
       "codes": [
          "41C0723E90FC4E99B21C7106CE8224BE",
          "7F658DD412954E0DAFD6BA8EC09AFFF8",
          "39B03E903A4645B282166CB18FADB956",
          "44BB9BB199C64C65A95940A05D2142EB",
          "6A244FAF62114238B63A0EF3FFBB0066"
       ]
    }
}
```

### /setup_mfa
Accepts **POST**. Requires body:

```json
{
    "mfa_enabled": true,
    "otp": 12345
}
```
**otp** is required only for mfa enabling

Returns in case of success:
```json
{
    "message": "MFA enabled successfully",
    "success": true
}
```

### /recovery_codes
Accepts **GET** and  **POST**. 

**GET** returns already existing codes while **POST** recreates and returns codes

Returns in case of success:
```json
{
    "data": [
        "A6EA675CA07F4D2ABFCE9344E88C75A7",
        "709B2E3065844D14864BCDE6C0518CCE",
        "4847A940741146B9BB2C53BB428B9E60",
        "E6E2FE50226D4C1BAF116BF43082415F"
    ],
    "success": true
}
```

### /verify_recovery_code
Accepts **POST**. Requires body:

```json
{
    "email": "email",
    "recovery_code": "A6EA675CA07F4D2ABFCE9344E88C75A7"
}
```

Returns in case of success:
```json
{
    "message": "The MFA recovery code is valid",
    "success": true,
    "user": {
        "access_token": "AccessToken",
        "active": 1,
        "email": "test@test.com",
        "entity_id": "",
        "first_name": "Deepak",
        "last_name": "Paudel",
        "latest": 1,
        "login_method": null,
        "verified": 1,
        "verified_on": 1638982653,
        "mfa_enabled": true,
        "expires_in": 1640629460
  }
}
```


### /login_mfa
Accepts **POST**. Requires body:

```json
{
    "email": "email",
    "otp": 123456
}
```

Returns in case of success:
```json
{
    "message": "The TOTP MFA token is valid",
    "success": true,
    "user": {
        "access_token": "AccessToken",
        "active": 1,
        "email": "test@test.com",
        "entity_id": "",
        "first_name": "Deepak",
        "last_name": "Paudel",
        "latest": 1,
        "login_method": null,
        "verified": 1,
        "verified_on": 1638982653,
        "mfa_enabled": true,
        "expires_in": 1640629460
  }
}
```

### /social
**Login is required.**
Accepts **GET**.

GET returns list of login methods:
```json
{
    "login_methods": [
        {
            "profile": {
                "access_token": "github_access_token",
                "email": "user@email.com",
                "entity_id": "0934ed3eccc245af9467c71f6fcecefa",
                "expires_in": null,
                "name": "github",
                "refresh_token": null,
                "refresh_token_expires_in": null,
                "scope": "user",
                "token_type": "bearer",
                "user_name": "Dinara"
            },
            "provider": "github"
        },
        {
            "profile": {
                "access_token": "google_access_token",
                "email": "user@email.com",
                "entity_id": "8e816d660ae14abea3ae58d6e76b01fc",
                "expires_in": 1639407953,
                "name": "google",
                "refresh_token": null,
                "refresh_token_expires_in": null,
                "scope": null,
                "token_type": null,
                "user_name": "S Dinara"
            },
            "provider": "google"
        },
        {
            "profile": {
                "access_token": null,
                "email": null,
                "entity_id": "b152d054b9c4432789a0ab60bbfd3480",
                "expires_in": null,
                "name": "signup",
                "refresh_token": null,
                "refresh_token_expires_in": null,
                "scope": null,
                "token_type": null,
                "user_name": null
            },
            "provider": "signup"
        }
    ],
    "success": true
}
```

### /social/{uuid}
**Login is required.**
Accepts **DELETE**.

DELETE returns in case of success:
```json
{
    "message": "Login method is deleted",
    "success": true
}
```
DELETE returns in case of error:
```json
{
    "message": "This user doesn't have login method 7bc8d6066dad49bc889563af3831ab64",
    "success": false
}
```

### /social/github
Accepts **POST**. Requires body:
```json
{
    "code": "4b7c12a88b108f36a78b"
}
```
If Authorization header is set then github account will be connected to logged in user.

Returns:
```json
{
    "auth": {
        "access_token": "github_access_token",
        "scope": "user",
        "token_type": "bearer"
    },
    "success": true,
    "user": {
        "access_token": "flask_access_token",
        "active": 1,
        "email": "user@email.com",
        "entity_id": "50bc97273e08473b97ea973701cc832c",
        "first_name": "Dinara",
        "last_name": null,
        "latest": 1,
        "login_method": null,
        "verified": 0,
        "verified_on": null,
        "mfa_enabled": false,
        "expires_in": 1640629460
    }
}
```


### /social/google
Accepts **POST**. Requires body:
```json
{
    "idtoken": "idtoken"
}
```
If Authorization header is set then google account will be connected to logged in user.

Returns:
```json
{
    "auth": {
        "access_token": "google_id_token",
        "expires_in": 1639381840,
        "name": "google",
        "sub": "113197524860174073434"
    },
    "success": true,
    "user": {
        "access_token": "flask_access_token",
        "active": true,
        "email": "user@email.com",
        "entity_id": "d8e21a9c70774e2bb6f28d546365827b",
        "first_name": "S",
        "last_name": "Dinara",
        "latest": true,
        "login_method": null,
        "verified": true,
        "verified_on": null,
        "mfa_enabled": false,
        "expires_in": 1640629460
    }
}
```


### /social/linkedin
Accepts **POST**. Requires body:
```json
{
    "code": "ce7b4c63f60fccc8ba50"
}
```
If Authorization header is set then google account will be connected to logged in user.

Returns:
```json
{
    "auth": {
        "access_token": "linkedin_access_token",
        "expires_in": 5183999,
        "name": "linkedin"
    },
    "success": true,
    "user": {
        "access_token": "flask_access_token",
        "active": true,
        "email": "user@email.com",
        "entity_id": "5f12544303f94fe889c5574eccd3751e",
        "first_name": "Dinara",
        "last_name": "Sultangulova",
        "latest": true,
        "verified": false,
        "verified_on": null, 
        "mfa_enabled": false,
        "expires_in": 1640629460
    }
}
```


### /social/facebook
Accepts **POST**. Requires body:
```json
{
    "accessToken": "token",
    "data_access_expiration_time": 1652186921,
    "expiresIn": 4279,
    "grantedScopes": "email,public_profile",
    "userID": "userId",
    "email": "user@mail.com",
    "name": "Dinara S"
}
```
If Authorization header is set then facebook account will be connected to logged in user.

Returns:
```json
{
    "auth": {
        "access_token": "facebook_token",
        "data_access_expiration_time": 1652186921,
        "email": "user@mail.com",
        "expires_in": 4279,
        "name": "facebook",
        "scope": "email,public_profile",
        "user_name": "Dinara S"
    },
    "success": true,
    "user": {
        "access_token": "flask_access_token",
        "active": true,
        "email": "user@mail.com",
        "entity_id": "5f867a3b061e4e5c937d5e9a942f95cc",
        "expires_in": 1644414863,
        "first_name": "Dinara",
        "last_name": "S",
        "latest": true,
        "mfa_enabled": false,
        "verified": false,
        "verified_on": null
    }
}
```


</details>


## Tests
<details>
  <summary><b>How to run</b></summary>

To run tests use the following command in the api container:
```shell
coverage run -m pytest
```

To see coverage report use:
```shell
 coverage report
 ```
</details>
