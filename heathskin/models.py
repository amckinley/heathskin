
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


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blizz_id = db.Column(db.String(32), unique=True, nullable=False)

class GameHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    won = db.Column(db.Boolean())
    hero = db.Column(db.String(255), nullable=False)
    opponent = db.Column(db.String(255), nullable=False)
    hero_health = db.Column(db.Integer)
    enemy_health = db.Column(db.Integer)
