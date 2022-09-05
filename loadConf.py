from configparser import ConfigParser
from urllib.parse import urlparse
import os


db = urlparse(os.environ.get('CLEARDB_DATABASE_URL'))


parser = ConfigParser()
parser.read('configurations.ini')


def get_bot_token():
    return parser.get('bot', 'token')


def get_dev_bot_token():
    return parser.get('devbot', 'token')


def get_database_user():
    return db.username


def get_dev_database_user():
    return parser.get('devdatabase', 'user')


def get_database_pass():
    return db.password


def get_database_host():
    return os.environ.get('CLEARDB_DATABASE_CLEARDB_HOSTNAME_1', 'mysql://localhost:3306/whatsappbot')
    # return db.hostname


def get_database_name():
    return db.path.lstrip('/')


def get_dev_database_host():
    return parser.get('devdatabase', 'host')


def get_twilio_sid():
    return parser.get('twilio', 'account_sid')


def get_twilio_auth_token():
    return parser.get('twilio', 'auth_token')
