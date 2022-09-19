from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(test=False):
    app = Flask(__name__)

    db.init_app(app)

    if test:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.site.sqlite'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.sqlite'

    from grants.households.routes import households

    app.register_blueprint(households)

    with app.app_context():
        db.create_all()
    return app
