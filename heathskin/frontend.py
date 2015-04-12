#!/usr/bin/env python

import json
from datetime import datetime
import pickle
import argparse
import sys

import logging
from logging import StreamHandler, Formatter

from flask import Flask, render_template, session, request, \
    jsonify, abort, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, auth_token_required
from flask.ext.login import current_user


from heathskin import game_state
from heathskin import game_universe, card_database


# Create app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False

# XXX: hurr durr security is hard
app.config['WTF_CSRF_ENABLED'] = False

# Create database connection object
db = SQLAlchemy(app)

logger = app.logger

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

# cards_decks = db.Table('cards_decks',
#         db.Column('card_id', db.Integer(), db.ForeignKey('card.id')),
#         db.Column('deck_id', db.Integer(), db.ForeignKey('deck.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


class CardDeckAssociation(db.Model):
    __tablename__ = 'cards_decks'
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), primary_key=True)
    count = db.Column(db.Integer)
    deck = db.relationship("Deck", backref="deck")


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blizz_id = db.Column(db.String(255), unique=True)

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    #children = relationship("Association", backref="parent")
    cards = db.relationship("CardDeckAssociation")
    # cards  = db.relationship('Card', secondary=cards_decks,
    #                         backref=db.backref('decks', lazy='dynamic'))

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

SESSION_LOG_ROOT = "session_logs"
GAME_UNIVERSE = game_universe.GameUniverse(session_log_path=SESSION_LOG_ROOT)

def get_server_for_user(user_id):
    return "web1"
    #username = request.cookies.get('username')


def get_game_state(user_id):
    #session_start = session['session_start_time']
    game_state = GAME_UNIVERSE.get_latest_game_state_for_user(user_id)
    return game_state

@app.route('/entity_dump')
@login_required
def entity_dump():
    game_state = get_game_state(current_user.get_id())
    return str(set([e.card_id for e in game_state.entities.values()]))

@app.route("/tracker")
@login_required
def deck_tracker():
    card_db = card_database.CardDatabase.get_database()
    game_state = get_game_state(current_user.get_id())
    if not game_state:
        return "no game states found for user id {}".format(current_user.get_id())

    hand = game_state.get_friendly_hand()
    hand_ids = [card_db.get_card_by_id(e.card_id) for e in hand]
    return render_template('jquerytest.html',
                            cards=hand_ids,
                            handsize=len(hand_ids))


@app.route('/upload_line', methods=['POST'])
@auth_token_required
def upload_line():
    if 'session_start_time' not in session:
        abort(400)

    # this is where we actually update the game with the incoming log line
    GAME_UNIVERSE.feed_line(
        user_id=current_user.get_id(),
        session_start=session['session_start_time'],
        log_line=request.get_json()["log_line"])

    logger.debug("got a log line from user %s", current_user.get_id())
    return ''

@app.route('/start_session', methods=['POST'])
@auth_token_required
def start_session():
    session['session_start_time'] = datetime.now().replace(microsecond=0).isoformat()
    latest_session_key = "latest_session_start_{}".format(current_user.get_id())

    # magical persistence cookie
    resp = make_response("")
    resp.set_cookie('FOO', get_server_for_user(current_user.get_id()))

    logger.info("starting session for user %s", current_user.get_id())
    return resp

@app.route('/api/help', methods = ['GET'])
def help():
    """Print available functions."""
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)





