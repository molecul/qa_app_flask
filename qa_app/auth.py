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
import settings

from qa_app import google
from qa_app import models

from flask import current_app as app, Blueprint, session, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user

import json

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

    if access_token is None:
        return redirect(url_for('auth.login'))

    from urllib2 import Request, urlopen, URLError

    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('auth.login'))
        return res.read()

    info = json.loads(res.read())

    for current in info.keys():
        session[current] = info[current]

    if session['email'] is None or session['email'] == "":
        return redirect(url_for('auth.login'))

    user = models.Users.query.filter_by(email=info['email']).first()
    if user is None:
        uuid = info['id']
        user = models.Users(uuid=uuid, name=info['name'], email=info['email'], role=settings.USER_ROLE['user'])
        models.db.session.add(user)
        models.db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    session['username'] = user.name
    session['admin'] = user.role
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('views.index'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')


@auth.route('/logout', strict_slashes=False)
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('views.index'))
