from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from datetime import timedelta
from loguru import logger

app = Flask(__name__)
CORS(app)

if os.environ.get('ENV') == 'PROD':
    from config.config_prod import Config
else:
    from config.config_dev import Config
app.config.from_object(Config)

if not app.config['SECRET_KEY']:
    logger.error('请设置 SECRET_KEY 环境变量以确保 session 加密安全。')
    exit()

if not os.path.exists('flask_session'):
    os.mkdir('flask_session')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=3)
Session(app)

limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app=app)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

db = SQLAlchemy(app)

from .routes import main
from .User.routes import user
from .File.routes import file
app.register_blueprint(main, url_prefix='/')
app.register_blueprint(user, url_prefix='/user')
app.register_blueprint(file, url_prefix='/file')

@app.errorhandler(429) #急急国王
def over_per(code):
    return {
        'code': 429,
        'errno': 429,
        'msg': "TOO_MANY_REQUESTS"   
    }, 429