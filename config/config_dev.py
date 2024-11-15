from config.config_prod import config

class config(config):
    DEBUG = True
    RUN_PORT = '5050'
    PG_SERVER = 'localhost'
    PG_PORT = 5432
    PG_USER = 'postgres'
    PG_PWD = 'postgres'
    PG_DB = 'test'
    SECRET_KEY = '6aefbbe0c9ad25d29c5a6ddcda1ee217b5cc572fe1a350cd30be327ca38ef5a2' # echo HiTorch | sha256sum -
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(PG_USER,PG_PWD,PG_SERVER,PG_PORT,PG_DB)

Config = config