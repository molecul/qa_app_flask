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


db = SQLAlchemy()


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(128), unique=True)
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
    return '<User %r>' % (self.name)