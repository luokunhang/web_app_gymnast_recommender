import os
DEBUG = True
LOGGING_CONFIG = "config/logging/local.conf"
PORT = 5000
APP_NAME = "gym_match"
SQLALCHEMY_TRACK_MODIFICATIONS = True
HOST = '0.0.0.0'
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 5

SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
if not SQLALCHEMY_DATABASE_URI:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/gymnastics.db'
