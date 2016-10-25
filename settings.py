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
import os

##### GENERATE SECRET KEY #####
with open('.qa_app_secret_key', 'a+') as secret:
    secret.seek(0)  # Seek to beginning of file since a+ mode leaves you at the end and w+ deletes the file
    key = secret.read()
    if not key:
        key = os.urandom(64)
        secret.write(key)
        secret.flush()


##### SERVER SETTINGS #####
DEBUG = True
SECRET_KEY = key
SQLALCHEMY_DATABASE_URI = 'sqlite:///qa_app_database.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SESSION_TYPE = "filesystem"
SESSION_FILE_DIR = "/tmp/flask_session"
SESSION_COOKIE_HTTPONLY = True
PERMANENT_SESSION_LIFETIME = 604800 # 7 days in seconds
HOST = "localhost"
UPLOAD_FOLDER = os.path.normpath('static/uploads')
TEMPLATE = 'original'
TEMPLATES_AUTO_RELOAD = True
TRUSTED_PROXIES = [
    '^127\.0\.0\.1$',
    # Remove the following proxies if you do not trust the local network
    '^::1$',
    '^fc00:',
    '^10\.',
    '^172\.(1[6-9]|2[0-9]|3[0-1])\.',
    '^192\.168\.'
]
# admin list
# (needs only for first log in, manage by user -> is_admin)
ADMINS = ['user@domain.com']
USER_ROLE = {'user': 0, 'admin': 1}


##### AUTH SETTINGS #####
# You must configure these 3 values from Google APIs console
# https://code.google.com/apis/console
GOOGLE_CLIENT_ID = '<Client-ID>'
GOOGLE_CLIENT_SECRET = '<Client-secret>'
REDIRECT_URI = '/authorized'  # one of the Redirect URIs from Google APIs console
