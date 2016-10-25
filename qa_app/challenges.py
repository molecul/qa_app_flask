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
from flask import Blueprint, render_template, jsonify, session, redirect, url_for, request
import re
import json
from qa_app.models import db, Challenges,Tags, Files, Solves, Users, Awards
from qa_app.utils import authed, unix_time, is_admin, get_ip

from sqlalchemy.sql import and_, or_, not_

challenges = Blueprint('challenges', __name__)


@challenges.route('/challenges', methods=['GET'])
def challenges_view():
    return render_template('chals.html', page="Challenges")


@challenges.route('/chals', methods=['GET'])
def chals():
    chals = Challenges.query.filter(or_(Challenges.hidden != True, Challenges.hidden == None)).add_columns('id', 'name', 'value', 'description', 'category').order_by(Challenges.value).all()

    json = {'game':[]}
    for x in chals:
        tags = [tag.tag for tag in Tags.query.add_columns('tag').filter_by(chal=x[1]).all()]
        files = [ str(f.location) for f in Files.query.filter_by(chal=x.id).all() ]
        json['game'].append({'id':x[1], 'name':x[2], 'value':x[3], 'description':x[4], 'category':x[5], 'files':files, 'tags':tags})

    db.session.close()
    return jsonify(json)


@challenges.route('/chals/solves')
def chals_per_solves():
    solves_sub = db.session.query(Solves.chalid, db.func.count(Solves.chalid).label('solves')).join(Users, Solves.userid == Users.id).filter(Users.banned == False).group_by(Solves.chalid).subquery()
    solves = db.session.query(solves_sub.columns.chalid, solves_sub.columns.solves, Challenges.name) \
        .join(Challenges, solves_sub.columns.chalid == Challenges.id).all()
    json = {}
    for chal, count, name in solves:
        json[name] = count
    db.session.close()
    return jsonify(json)


@challenges.route('/solves')
@challenges.route('/solves/<userid>')
def solves(userid=None):
    solves = None
    awards = None
    if userid is None:
        if is_admin():
            solves = Solves.query.filter_by(userid=session['id']).all()
        elif authed():
            solves = Solves.query.join(Users, Solves.userid == Users.id).filter(Solves.userid == session['id'], Users.banned == False).all()
        else:
            return redirect(url_for('auth.login', next='solves'))
    else:
        solves = Solves.query.filter_by(userid=userid).all()
        awards = Awards.query.filter_by(userid=userid).all()
    db.session.close()
    json = {'solves':[]}
    for solve in solves:
        json['solves'].append({
            'chal': solve.chal.name,
            'chalid': solve.chalid,
            'user': solve.userid,
            'value': solve.chal.value,
            'category': solve.chal.category,
            'time': unix_time(solve.date)
        })
    if awards:
        for award in awards:
            json['solves'].append({
                'chal': award.name,
                'chalid': None,
                'user': award.userid,
                'value': award.value,
                'category': award.category,
                'time': unix_time(award.date)
            })
    json['solves'].sort(key=lambda k: k['time'])
    return jsonify(json)


@challenges.route('/chal/<chalid>/solves', methods=['GET'])
def who_solved(chalid):
    solves = Solves.query.join(Users, Solves.userid == Users.id).filter(Solves.chalid == chalid, Users.banned == False).order_by(Solves.date.asc())
    json = {'users':[]}
    for solve in solves:
        json['users'].append({'id':solve.user.id, 'name':solve.user.name, 'date':solve.date})
    return jsonify(json)


@challenges.route('/chal/<chalid>', methods=['POST'])
def chal(chalid):
    if authed():
        solves = Solves.query.filter_by(userid=session['id'], chalid=chalid).first()
        # Challange not solved yet
        if not solves:
            chal = Challenges.query.filter_by(id=chalid).first()
            key = str(request.form['key'].strip().lower())
            keys = json.loads(chal.flags)

            for x in keys:
                if x['type'] == 0: #static key
                    print(x['flag'], key.strip().lower())
                    if x['flag'] and x['flag'].strip().lower() == key.strip().lower():
                        solve = Solves(chalid=chalid, userid=session['id'], ip=get_ip(), flag=key)
                        db.session.add(solve)
                        db.session.commit()
                        db.session.close()
                        # logger.info("[{0}] {1} submitted {2} with kpm {3} [CORRECT]".format(*data))
                        # return "1" # key was correct
                        return jsonify({'status':'1', 'message':'Correct'})
                elif x['type'] == 1: #regex
                    res = re.match(str(x['flag']), key, re.IGNORECASE)
                    if res and res.group() == key:
                        solve = Solves(chalid=chalid, userid=session['id'], ip=get_ip(), flag=key)
                        db.session.add(solve)
                        db.session.commit()
                        db.session.close()
                        # logger.info("[{0}] {1} submitted {2} with kpm {3} [CORRECT]".format(*data))
                        # return "1" # key was correct
                        return jsonify({'status': '1', 'message': 'Correct'})
            # logger.info("[{0}] {1} submitted {2} with kpm {3} [WRONG]".format(*data))
            # return '0' # key was wrong
            return jsonify({'status': '0', 'message': 'Incorrect'})


        # Challenge already solved
        else:
            #logger.info("{0} submitted {1} with kpm {2} [ALREADY SOLVED]".format(*data))
            # return "2" # challenge was already solved
            return jsonify({'status': '2', 'message': 'You already solved this'})
    else:
        return "-1"