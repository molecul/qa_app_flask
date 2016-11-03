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

from flask import Blueprint, render_template, jsonify, abort
from flask_login import login_required

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


@challenges.route('/challenge/<task>', method=['GET'])
@login_required
def challenge_view(task):
    return render_template('challenge.html', page=task)


@challenges.route('/exercise/<task>', methods=['GET'])
@login_required
def api_exercise(task):
    exercises = requests.get("http://localhost:8000/exercises").json()
    for current in exercises['exercises']:
        if current.get('name', None) == task:
            return jsonify(current)
    return abort(404)
