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

from flask_sqlalchemy import SQLAlchemy

from socket import inet_aton, inet_ntoa
from struct import unpack, pack, error as struct_error

import datetime
import json

db = SQLAlchemy()


def ip2long(ip):
    return unpack('!i', inet_aton(ip))[0]


def long2ip(ip_int):
    try:
        return inet_ntoa(pack('!i', ip_int))
    except struct_error:
        # Backwards compatibility with old databases
        return inet_ntoa(pack('!I', ip_int))


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(128), unique=True)
    name = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True)
    role = db.Column(db.SmallInteger, default=settings.USER_ROLE['user'])
    banned = db.Column(db.Boolean, default=False)

    @property
    def is_admin(self):
        if self.email in settings.ADMINS or self.role:
            return True
        else:
            return False

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        if self.banned:
            return False
        else:
            return True

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<user %r>' % (self.email.split('@')[0])

    def score(self):
        score = db.func.sum(Challenges.value).label('score')
        user = db.session.query(Solves.userid, score).join(Users).join(Challenges).filter(Users.banned == False, Users.id==self.id).group_by(Solves.userid).first()
        award_score = db.func.sum(Awards.value).label('award_score')
        award = db.session.query(award_score).filter_by(userid=self.id).first()
        if user:
            return int(user.score or 0) + int(award.award_score or 0)
        else:
            return 0

    def place(self):
        score = db.func.sum(Challenges.value).label('score')
        quickest = db.func.max(Solves.date).label('quickest')
        users = db.session.query(Solves.userid).join(Users).join(Challenges).filter(Users.banned == False).group_by(Solves.userid).order_by(score.desc(), quickest).all()
        #http://codegolf.stackexchange.com/a/4712
        try:
            i = users.index((self.id,)) + 1
            k = i % 10
            return "%d%s" % (i, "tsnrhtdd"[(i / 10 % 10 != 1) * (k < 4) * k::4])
        except ValueError:
            return 0


class Challenges(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.Text)
    value = db.Column(db.Integer)
    category = db.Column(db.String(80))
    flags = db.Column(db.Text)
    hidden = db.Column(db.Boolean)

    def __init__(self, name, description, value, category, flags):
        self.name = name
        self.description = description
        self.value = value
        self.category = category
        self.flags = json.dumps(flags)

    def __repr__(self):
        return '<chal %r>' % self.name


class Awards(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(80))
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    value = db.Column(db.Integer)
    category = db.Column(db.String(80))
    icon = db.Column(db.Text)

    def __init__(self, userid, name, value):
        self.userid = userid
        self.name = name
        self.value = value

    def __repr__(self):
        return '<award %r>' % self.name


class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chal = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    tag = db.Column(db.String(80))

    def __init__(self, chal, tag):
        self.chal = chal
        self.tag = tag

    def __repr__(self):
        return "<Tag {0} for challenge {1}>".format(self.tag, self.chal)


class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chal = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    location = db.Column(db.Text)

    def __init__(self, chal, location):
        self.chal = chal
        self.location = location

    def __repr__(self):
        return "<File {0} for challenge {1}>".format(self.location, self.chal)


class Solves(db.Model):
    __table_args__ = (db.UniqueConstraint('chalid', 'userid'), {})
    id = db.Column(db.Integer, primary_key=True)
    chalid = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    userid = db.Column(db.Integer, db.ForeignKey('users.id'))
    ip = db.Column(db.Integer)
    flag = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship('Users', foreign_keys="Solves.userid", lazy='joined')
    chal = db.relationship('Challenges', foreign_keys="Solves.chalid", lazy='joined')
    # value = db.Column(db.Integer)

    def __init__(self, chalid, userid, ip, flag):
        self.ip = ip2long(ip)
        self.chalid = chalid
        self.userid = userid
        self.flag = flag
        # self.value = value

    def __repr__(self):
        return '<solves %r>' % self.chal
