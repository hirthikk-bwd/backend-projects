import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object("app.config.Config")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.auth import auth_bp
    from app.jobs import jobs_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(jobs_bp, url_prefix="/jobs")

    @app.route("/")
    def index():
        return jsonify(
            {
                "service": "Job Tracker API",
                "version": "1.0",
                "endpoints": {
                    "register": "POST /auth/register",
                    "login": "POST /auth/login",
                    "jobs": "GET/POST /jobs/",
                    "job": "PUT/DELETE /jobs/<id>",
                },
                "status": "running",
            }
        )

    return app
