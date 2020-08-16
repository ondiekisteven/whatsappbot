from configparser import ConfigParser


parser = ConfigParser()
parser.read('configurations.ini')


def get_bot_token():
    return parser.get('bot', 'token')


def get_dev_bot_token():
    return parser.get('devbot', 'token')


def get_database_user():
    return parser.get('database', 'user')


def get_dev_database_user():
    return parser.get('devdatabase', 'user')


def get_database_pass():
    return parser.get('database', 'pass')


def get_database_host():
    return parser.get('database', 'host')


def get_dev_database_host():
    return parser.get('devdatabase', 'host')


def get_twilio_sid():
    return parser.get('twilio', 'account_sid')


def get_twilio_auth_token():
    return parser.get('twilio', 'auth_token')
