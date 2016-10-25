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
from flask import Blueprint, session, render_template
from flask_login import login_required

views = Blueprint('views', __name__)


@views.route('/')
def index():
    username = session.get('given_name', None)
    if username:
        return render_template("base.html", page="Main", username=username)
    else:
        return render_template("base.html", page="Main")


@views.route('/profile')
@login_required
def profile():
    return render_template("profile.html",
                           page="Profile",
                           id=session['id'],
                           username=session['given_name'],
                           name=session['name'],
                           pic=session['picture']
                           )
