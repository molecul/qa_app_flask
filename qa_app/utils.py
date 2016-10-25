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
import os
import datetime
import hashlib
import re

from socket import inet_aton, inet_ntoa, socket
from struct import unpack, pack

from qa_app import models, lm
from flask import current_app as app, g, session, request, abort
from flask_login import current_user

import settings


@app.before_request
def before_request():
    g.user = current_user


@lm.user_loader
def load_user(id):
    return models.Users.query.get(int(id))


def authed():
    return bool(session.get('id', False))


def unix_time(dt):
    return int((dt - datetime.datetime(1970, 1, 1)).total_seconds())


def unix_time_millis(dt):
    return unix_time(dt) * 1000


def sha512(string):
    return hashlib.sha512(string).hexdigest()


def get_ip():
    """ Returns the IP address of the currently in scope request. The approach is to define a list of trusted proxies
     (in this case the local network), and only trust the most recently defined untrusted IP address.
     Taken from http://stackoverflow.com/a/22936947/4285524 but the generator there makes no sense.
     The trusted_proxies regexes is taken from Ruby on Rails.
     This has issues if the clients are also on the local network so you can remove proxies from config.py.
     QATrainingFrontend does not use IP address for anything besides cursory tracking of users and it is ill-advised to do much
     more than that if you do not know what you're doing.
    """
    trusted_proxies = app.config['TRUSTED_PROXIES']
    combined = "(" + ")|(".join(trusted_proxies) + ")"
    route = request.access_route + [request.remote_addr]
    for addr in reversed(route):
        if not re.match(combined, addr): # IP is not trusted but we trust the proxies
            remote_addr = addr
            break
    else:
        remote_addr = request.remote_addr
    return remote_addr


def long2ip(ip_int):
    return inet_ntoa(pack('!I', ip_int))


def ip2long(ip):
    return unpack('!I', inet_aton(ip))[0]


def init_utils(app):
    app.jinja_env.filters['unix_time'] = unix_time
    app.jinja_env.filters['unix_time_millis'] = unix_time_millis
    app.jinja_env.filters['long2ip'] = long2ip
    app.jinja_env.globals.update(template_theme=settings.TEMPLATE)

    @app.context_processor
    def inject_user():
        if session:
            return dict(session)
        return dict()

    @app.before_request
    def csrf():
        if not session.get('nonce'):
            session['nonce'] = sha512(os.urandom(10))
        if request.method == "POST":
            if session['nonce'] != request.form.get('nonce'):
                abort(403)
