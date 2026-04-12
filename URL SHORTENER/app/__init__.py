import redis as redis_client
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_name='default'):
    app = Flask(__name__)

    from config import config
    app.config.from_object(config[config_name])

    db.init_app(app)

    app.redis = redis_client.from_url(
        app.config['REDIS_URL'],
        decode_responses=True
    )

    from app.routes import bp
    app.register_blueprint(bp)

    return app
