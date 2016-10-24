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
from qa_app import google

from flask import current_app as app, Blueprint, session, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    callback = url_for('auth.authorized', _external=True)
    return google.authorize(callback=callback)


@auth.route(app.config['REDIRECT_URI'])
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('views.index'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')


@auth.route('/logout', strict_slashes=False)
def logout():
    logout_user()
    return redirect(url_for('views.index'))
