from app import app
from loguru import logger

if __name__ == '__main__':
    app.run(host=app.config['RUN_HOST'], port=app.config['RUN_PORT'])