import os


class Config(object):
    STAGE = os.environ.get('STAGE')
    FLASK_ENV = os.environ.get("FLASK_ENV")
    DEBUG = False
    TESTING = False
    ACCESS_TOKEN_EXPIRE = os.environ.get('ACCESS_TOKEN_EXPIRE')
    MIME_TYPE = 'application/json'

    FRONTEND_URL = os.environ.get("VUE_APP_URI")
    SOCIAL_AUTH_REDIRECT_URI = os.environ.get("VUE_APP_SOCIAL_AUTH_REDIRECT_URI")

    # MYSQL CONFIGS
    MYSQL_HOST = os.environ.get("MYSQL_HOST")
    MYSQL_USER = os.environ.get("MYSQL_USER")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
    MYSQL_PORT = os.environ.get("MYSQL_PORT")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")

    # RabbitMQ CONFIGS
    BROKER_PATH = os.environ.get('BROKER_PATH', 'rabbitmq:5672')
    RABBITMQ_USER = os.environ.get('RABBITMQ_USER')
    RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD')
    RABBITMQ_VHOST = os.environ.get('RABBITMQ_VHOST')
    MQ_URL = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{BROKER_PATH}/{RABBITMQ_VHOST}'
    MQ_EXCHANGE = os.environ.get('MQ_EXCHANGE')

    # SOCIAL AUTH
    GITHUB_OAUTH_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
    GITHUB_OAUTH_CLIENT_SECRET = os.environ.get('GITHUB_OAUTH_CLIENT_SECRET')
    GITHUB_OAUTH_URL = 'https://github.com/login/oauth/access_token'
    GITHUB_USER_INFO_URL = 'https://api.github.com/user'

    LINKEDIN_OAUTH_CLIENT_ID = os.environ.get('LINKEDIN_CLIENT_ID')
    LINKEDIN_OAUTH_CLIENT_SECRET = os.environ.get('LINKEDIN_OAUTH_CLIENT_SECRET')
    LINKEDIN_OAUTH_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
    LINKEDIN_USER_INFO_URL = 'https://api.linkedin.com/v2/me'
    LINKEDIN_USER_EMAIL_URL = 'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))'

    GOOGLE_OAUTH_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')

    # ROLLBAR
    ROLLBAR_ACCESS_TOKEN = os.environ.get('ROLLBAR_ACCESS_TOKEN')

    # Pusher
    PUSHER_APP_ID = os.environ.get('PUSHER_APP_ID')
    PUSHER_API_KEY = os.environ.get('PUSHER_API_KEY')
    PUSHER_API_SECRET = os.environ.get('PUSHER_API_SECRET')
    PUSHER_CLUSTER = os.environ.get('PUSHER_CLUSTER')


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
    OAUTHLIB_INSECURE_TRANSPORT = False


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = "secret_for_test_environment"
    SECURITY_PASSWORD_SALT = "password_salt_for_dev"
    OAUTHLIB_INSECURE_TRANSPORT = True  # do not use in prod


class TestConfig(Config):
    FLASK_ENV = 'test'
    DEVELOPMENT = True
    DEBUG = True
    TESTING = True
    SECRET_KEY = "secret_for_test_environment"
    SECURITY_PASSWORD_SALT = "password_salt_for_test"
    OAUTHLIB_INSECURE_TRANSPORT = True  # do not use in prod
    # MYSQL CONFIGS
    MYSQL_HOST = os.environ.get("MYSQL_TEST_HOST", 'localhost')
    MYSQL_USER = os.environ.get("MYSQL_USER")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
    MYSQL_PORT = os.environ.get("MYSQL_TEST_PORT", 3307)
    MYSQL_DATABASE = os.environ.get("MYSQL_TEST_DATABASE", 'test_core')
