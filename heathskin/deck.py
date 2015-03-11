from collections import defaultdict
import copy
import json
import operator
import logging

from heathskin import utils
from heathskin import card_database

def deck_from_file(path):
    with open(path) as f:
        card_names = [n.rstrip() for n in f.readlines()]

    return Deck(card_names)

class Deck(object):
    def __init__(self, card_list):
        self.logger = logging.getLogger()
        if len(card_list) != 30:
            raise Exception("you must have exactly 30 cards; found {}".format(len(card_list)))

        self.card_list = card_list
        self.card_db = card_database.CardDatabase.get_database()

        collectible_card_names = [c['name'] for c in self.card_db.all_collectible_cards]
        for c in self.card_list:
            if c not in collectible_card_names:
                raise Exception("card is not valid: {}".format(c))

        print "no collectible", len(list(self.card_db.search(collectible=False)))
        print "collectible", len(list(self.card_db.search()))
        print "name match ortal", len(list(self.card_db.search(name='ortal')))
        print "cost match 7", len(list(self.card_db.search(cost=7)))
        print "type is minion", len(list(self.card_db.search(card_type="Minion")))
        print "rarity is legendary", len(list(self.card_db.search(rarity="Legendary")))
        print "faction is alliance", len(list(self.card_db.search(faction="Alliance")))

        print "taunters with 4 attack", len(list(self.card_db.search(attack=4, mechanics=['Taunt'])))



    def consume_card_by_name(self, card_name):
        if card_name in self.in_deck:
            self.in_deck.remove(card_name)
            self.consumed.append(card_name)
        else:
            print "couldnt find {}".format(card_name)

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

        sorted_probs = sorted(probs.items(), key=operator.itemgetter(1), reverse=True)
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
