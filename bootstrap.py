from collections import defaultdict

#from flask.ext.sqlalchemy import SQLAlchemy

from heathskin.frontend import db, Card, Deck, CardDeckAssociation, User
from heathskin import card_database

def create_deck(user, deck_path, card_db):
    with open(deck_path) as f:
        card_names = [n.rstrip() for n in f.readlines()]

    d = Deck(user=user)
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

    # for thing in d.cards:
    #     print thing.count, thing.card
    # #
    db.session.add(d)
    # print d.cards

def deck_id_to_card_list(deck_id, card_db):
    d = Deck.query.filter_by(id=deck_id).first()
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


def main():
    card_db = card_database.CardDatabase.get_database()
    # reset(card_db)
    # db.session.commit()

    # me_user = User.query.filter_by(id=1).first()
    # create_deck(me_user, "data/decks/handlock.deck", card_db)
    # db.session.commit()



    deck_id_to_card_list(1, card_db)

    print "\n\n\n"
    deck_id_to_card_list(2, card_db)





if __name__ == '__main__':
    main()