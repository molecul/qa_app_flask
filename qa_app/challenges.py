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

from flask import Blueprint, render_template, jsonify, abort, request, session
from flask_login import login_required, current_user

from qa_app.models import Users, Attempts
from qa_app import models

challenges = Blueprint('challenges', __name__)


@challenges.route('/challenges', methods=['GET'])
@login_required
def challenges_view():
    return render_template('challenges.html', page="Challenges")


@challenges.route('/exercises', methods=['GET'])
@login_required
def api_exercises():
    exercises = requests.get("http://localhost:8000/exercises").json()
    result = []
    for current in exercises['exercises']:
        result.append({
            "name": current.get('name', 'unknown'),
            "category": current.get('answers')[0].split(".")[1],
            "solved": 0,
            "cost": 100,
            "doc": current.get('doc', 'empty task'),
        })
    return jsonify(result)


@challenges.route('/solution/<task>/', methods=['POST'])
@login_required
def api_solution(task):
    from pprint import pprint

    exercises =\
        requests.get("http://localhost:8000/exercises").json()['exercises']
    exercise = next((ex for ex in exercises if ex['name'] == task))
    print(task)
    pprint(exercise)
    if exercise is None:
        return abort(404)
    if 'files[]' not in request.files:
        return abort(400)

    solution = request.files['files[]'].stream.read()
    answer = exercise['answers'][0]  # TODO: handle multiply answers?
    link = "http://localhost:8000/exercises/{0}".format(task)
    job_id = requests.post(link, json={answer: solution}).json()['id']
    user_id = Users.query.filter_by(email=session['email']).first().id

    attempt = Attempts(user_id=user_id, task_name=task, a_id=job_id)
    models.db.session.add(attempt)
    models.db.session.commit()

    return jsonify(user_id)
