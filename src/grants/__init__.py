from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://site.db'

    db.init_app(app)

    from grants.households.routes import households

    app.register_blueprint(households)

    return app
