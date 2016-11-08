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
from flask import Blueprint, render_template, request, session
from flask_login import login_required

from qa_app.models import Users, Attempts

views = Blueprint('views', __name__)


@views.before_request
def redirect_setup():
    if request.path.startswith("/static"):
        return


@views.route('/')
def index():
    return render_template("index.html", page="Home")


@views.route('/profile')
@login_required
def profile():
    user = Users.query(email=session['email']).first()
    attempts = Attempts.query(user_id=user.id).all()
    return render_template("profile.html", page="Profile", user=user, attempts=attempts)
