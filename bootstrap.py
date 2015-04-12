import os
from datetime import datetime
from collections import defaultdict

from heathskin.frontend import db, Card, Deck, \
    CardDeckAssociation, User
from heathskin import card_database

def create_deck(user, deck_path, card_db):
    with open(deck_path) as f:
        card_names = [n.rstrip() for n in f.readlines()]

    deck_name = os.path.basename(deck_path).split(".")[0]
    d = Deck(user_id=user.id, name=deck_name)
    card_counts = defaultdict(int)
    ids_to_objs = {}
    for n in card_names:
        res = card_db.search(name=n)
        if len(res) == 1:
            res = res[0]
            card_obj = Card.query.filter_by(blizz_id=res['id']).first()
            card_counts[card_obj.blizz_id] += 1
            ids_to_objs[card_obj.blizz_id] = card_obj
        else:
            raise Exception("couldnt find card with name {}".format(n))

    for blizz_id, cnt in card_counts.items():
        card_obj = ids_to_objs[blizz_id]
        cda = CardDeckAssociation(card=card_obj, deck=d, count=cnt)
        db.session.add(cda)

    db.session.add(d)

def deck_id_to_card_list(deck_id, card_db):
    d = Deck.query.filter_by(id=deck_id).first()
    print "deck:", d.name, d.user.email
    for c in d.cards:
        card = card_db.get_card_by_id(c.card.blizz_id)
        print card['name'], c.count

def add_card_data(card_db):
    for ent in card_db.all_collectible_cards:
        c = Card(blizz_id=ent['id'])
        db.session.add(c)

def reset(card_db):
    db.drop_all()
    db.create_all()
    add_card_data(card_db)
    make_default_users()

def make_default_users():
    austin = User(email="bearontheroof@gmail.com", password="wangwang", active=True, confirmed_at=datetime.now())
    andrew = User(email="andrewckoch@gmail.com", password="ninjacat", active=True, confirmed_at=datetime.now())
    peter = User(email="p@p.com", password="password", active=True, confirmed_at=datetime.now())
    db.session.add(austin)
    db.session.add(andrew)
    db.session.add(peter)


def main():
    card_db = card_database.CardDatabase.get_database()
    reset(card_db)
    db.session.commit()

    me_user = User.query.filter_by(id=1).first()
    create_deck(me_user, "data/decks/cwarrior.deck", card_db)
    create_deck(me_user, "data/decks/handlock.deck", card_db)
    db.session.commit()

    deck_id_to_card_list(1, card_db)
    print "\n\n\n"
    deck_id_to_card_list(2, card_db)


if __name__ == '__main__':
    main()
