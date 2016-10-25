#    Copyright 2016 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from flask import Flask
from flask_oauth import OAuth
from flask_login import LoginManager
from sqlalchemy_utils import database_exists, create_database

google = None

lm = LoginManager()


def create_app(config='settings'):
    app = Flask(__name__)
    with app.app_context():
        app.config.from_object(config)
        app.debug = app.config['DEBUG']
        app.secret_key = app.config['SECRET_KEY']

        from qa_app.models import db

        # sqlite database creation is relative to the script which causes issues with serve.py
        if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']) and not app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
            create_database(app.config['SQLALCHEMY_DATABASE_URI'])

        db.init_app(app)
        db.create_all()

        app.db = db

        oauth = OAuth()
        global google, lm
        lm.init_app(app)
        lm.login_view = 'auth.login'

        google = oauth.remote_app('google',
                                  base_url='https://www.google.com/accounts/',
                                  authorize_url='https://accounts.google.com/o/oauth2/auth',
                                  request_token_url=None,
                                  request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                        'response_type': 'code'},
                                  access_token_url='https://accounts.google.com/o/oauth2/token',
                                  access_token_method='POST',
                                  access_token_params={'grant_type': 'authorization_code'},
                                  consumer_key=app.config['GOOGLE_CLIENT_ID'],
                                  consumer_secret=app.config['GOOGLE_CLIENT_SECRET'])
        from qa_app import utils
        from qa_app import exceptions

        from qa_app.views import views
        from qa_app.auth import auth
        from qa_app.scoreboard import scoreboard
        from qa_app.challenges import challenges

        utils.init_utils(app)

        app.register_blueprint(views)
        app.register_blueprint(auth)
        app.register_blueprint(scoreboard)
        app.register_blueprint(challenges)

        return app
