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
from flask import Blueprint, render_template
from flask_login import login_required
from qa_app.models import Users

scoreboard = Blueprint('scoreboard', __name__)


@scoreboard.route('/scoreboard', defaults={'page':'1'})
@scoreboard.route('/scoreboard/<page>')
@login_required
def api_users(page):
    page = abs(int(page))
    results_per_page = 50
    page_start = results_per_page * ( page - 1 )
    page_end = results_per_page * ( page - 1 ) + results_per_page
    users = Users.query.slice(page_start, page_end).all()
    count = len(users)
    pages = int(count / results_per_page) + (count % results_per_page > 0)
    return render_template('scoreboard.html', page="Scoreboard", users=users, user_pages=pages, curr_page=page)