import os

class config(object):
    DEBUG = False
    TESTING = False
    RUN_HOST = '0.0.0.0'
    RUN_PORT = '5050'
    SECRET_KEY = os.environ.get('SECRET_KEY')
    PG_SERVER = os.getenv('PG_SERVER')
    PG_PORT = os.getenv('PG_PORT')
    PG_USER = os.getenv('PG_USER')
    PG_PWD = os.getenv('PG_PWD')
    PG_DB = os.getenv('PG_DB')
    SESSION_TYPE = 'filesystem'
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(PG_USER,PG_PWD,PG_SERVER,PG_PORT,PG_DB)

Config = config