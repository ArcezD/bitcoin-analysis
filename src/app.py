import os

from flask import Flask, request, jsonify

from .models import db
from .route.api import api as api_blueprint

# sqlite example
#basedir = os.path.abspath(os.path.dirname(__file__))
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ \
#                os.path.join(basedir, 'db.sqlite3')

def create_app(env_name, db_url):
    """
    Running app
    """

    # app initiliazation
    app = Flask(__name__)

    # initializing app config
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

    # register app routes
    app.register_blueprint(api_blueprint, url_prefix='/api/v1/note')

    return app