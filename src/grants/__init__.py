from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(test=False):
    app = Flask(__name__)

    if test:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../../tests/test.site.sqlite'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.sqlite'

    db.init_app(app)
    with app.app_context():
        db.create_all()

    from grants.households.routes import households

    app.register_blueprint(households)

    return app
