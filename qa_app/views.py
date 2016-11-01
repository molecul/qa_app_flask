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
import requests
from flask import Blueprint, session, render_template
from flask_login import login_required

views = Blueprint('views', __name__)


@views.route('/')
@login_required
def index():
    return render_template("profile.html", username=session['given_name'], name=session['name'], pic=session['picture'])


@views.route('/api/<cmd>')
@views.route('/api/<cmd>/<val>')
def training_proxy_get(cmd, val):
    build_url = "{base_url}"
    if cmd:
        build_url = "%s/{cmd}".format(cmd=cmd) % build_url
        if val:
            build_url = "%s/{val}".format(val=val) % build_url
    r = requests.get(build_url)
    if r.status_code == 200:
        return r.json()
    else:
        return r.content
