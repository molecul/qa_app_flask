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
from flask import Blueprint, session, render_template, request, jsonify
from flask_login import login_required, current_user

from qa_app.models import db, Users, Solves, Awards

views = Blueprint('views', __name__)


@views.before_request
def redirect_setup():
    if request.path.startswith("/static"):
        return


@views.route('/')
def index():
    return render_template("base.html", page="Main")


@views.route('/profile')
@login_required
def profile():
    return render_template("profile.html",
                           page="Profile",
                           username=session['given_name'],
                           name=session['name'],
                           pic=session['picture']
                           )


@views.route('/users', defaults={'page':'1'})
@views.route('/users/<page>')
def users(page):
    page = abs(int(page))
    results_per_page = 50
    page_start = results_per_page * ( page - 1 )
    page_end = results_per_page * ( page - 1 ) + results_per_page
    users = Users.query.slice(page_start, page_end).all()
    count = len(users)
    pages = int(count / results_per_page) + (count % results_per_page > 0)
    return render_template('users.html', users=users, user_pages=pages, curr_page=page)


@views.route('/user/<userid>', methods=['GET', 'POST'])
def user(userid):
    user = Users.query.filter_by(id=userid).first_or_404()
    solves = Solves.query.filter_by(userid=userid)
    awards = Awards.query.filter_by(userid=userid).all()
    score = user.score()
    place = user.place()
    db.session.close()

    if request.method == 'GET':
        return render_template('user.html', solves=solves, awards=awards, user=user, score=score, place=place)
    elif request.method == 'POST':
        json = {'solves':[]}
        for x in solves:
            json['solves'].append({'id':x.id, 'chal':x.chalid, 'user':x.userid})
        return jsonify(json)