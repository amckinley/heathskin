import copy
from collections import defaultdict
import operator

from datetime import datetime

from flask.ext.security import UserMixin, RoleMixin
from heathskin.frontend import db


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


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
    battletag = db.Column(db.String(255), unique=True)
    battlenet_id = db.Column(db.Integer, unique=True)


class CardDeckAssociation(db.Model):
    __tablename__ = 'cards_decks'
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), primary_key=True)
    count = db.Column(db.Integer, nullable=False)

    deck = db.relationship(
        'Deck', backref=db.backref("cards", cascade="all, delete-orphan"))
    card = db.relationship('Card')

    def __init__(self, card=None, deck=None, count=1):
        self.deck = deck
        self.card = card
        self.count = count


class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(255), nullable=False)
    user = db.relationship(
        'User', backref=db.backref("decks", cascade="all, delete-orphan"))

    def get_card_names(self):
        cards = []
        for id in self.blizz_ids:
            cards.append(id)
        return cards

    def print_draw_probs(self, deck, hand, play, graveyard):
        deck_size = len(deck)
        print "remaining cards: ", deck_size
        print "played cards: ", len(play + graveyard)

        not_possible = [c.name for c in hand + play + graveyard]
        probs = defaultdict(float)
        candidates = copy.copy(self.card_list)
        for c in not_possible:
            if c in candidates:
                candidates.remove(c)

        for c in candidates:
            probs[c] += 1.0 / len(candidates)
        counts = self.get_card_counts(candidates)

        sorted_probs = sorted(
            probs.items(), key=operator.itemgetter(1), reverse=True)
        for c, prob in sorted_probs:
            count_str = ""
            if counts[c] != 1:
                count_str = " (2x)"
            print (c + count_str).ljust(30), ":", "%.2f" % (prob * 100.0) + "%"

    def get_card_counts(self, cards):
        count_dict = defaultdict(int)
        for card in cards:
            count_dict[card] += 1
        return count_dict


    def get_remaining_cards(self, deck, game_state):
        friendly_entities = game_state.get_played_cards_friendly()
        unplayed_cards = deck.blizz_ids

        for entity in friendly_entities:
            if len(entity.card_id) == 0:
                break
            # XXX TODO doesn't work yet, still need to get the first zone set properly. filter to only cards played from deck
            if entity.get_source_zone():
                pass
            for b in deck.blizz_ids:
                card = card_db.get_card_by_id(b)
                if entity.card_id == card['id']:
                    unplayed_cards.remove(b)
            for b in unplayed_cards:
                card = card_db.get_card_by_id(b)

        return unplayed_cards


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blizz_id = db.Column(db.String(32), unique=True, nullable=False)


class GameHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    won = db.Column(db.Boolean())
    first = db.Column(db.Boolean())
    hero = db.Column(db.String(255), nullable=False)
    opponent = db.Column(db.String(255), nullable=False)
    hero_health = db.Column(db.Integer)
    enemy_health = db.Column(db.Integer)
    turns = db.Column(db.Integer)
    player1 = db.Column(db.String(255))
    player2 = db.Column(db.String(255))

    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
