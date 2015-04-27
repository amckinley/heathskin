#!/usr/bin/env python

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore


# Create app
app = Flask(
    __name__,
    static_url_path='',
    static_folder='../public',
    template_folder="../heathskin/templates")

app.config['SECRET_KEY'] = 'super-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False

# XXX: hurr durr security is hard
app.config['WTF_CSRF_ENABLED'] = False

import os
APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'public')

# Create database connection object
db = SQLAlchemy(app)

logger = app.logger

# we import down here to avoid the db object being unavailable. import
# of views module is required to actually add all the urls
from heathskin.models import User, Role
from heathskin import views  # noqa
from heathskin.api import views

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
