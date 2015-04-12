from collections import defaultdict
import copy
import operator
import logging

from heathskin import utils
from heathskin import card_database


def deck_from_path(path):
    with open(path) as f:
        # card_names = [n.rstrip() for n in f.readlines()]

        return deck_from_file(f)


def deck_from_file(deck_file):
    card_db = card_database.CardDatabase.get_database()
    card_list = list()
    for n in deck_file:
        card_name = n.rstrip()
        res = card_db.search(name=card_name)
        if len(res) == 1:
            card_list.append(res[0]['id'])
        else:
            raise Exception(
                "couldnt find card with name '{}'. len(res) = {}".format(
                    card_name, len(res)))

    return Deck(card_list)


class Deck(object):
    def __init__(self, blizz_ids):
        self.logger = logging.getLogger()
        if len(blizz_ids) != 30:
            raise Exception(
                "you must have exactly 30 cards; found {}".format(
                    len(blizz_ids)))
        self.blizz_ids = blizz_ids
        self.card_db = card_database.CardDatabase.get_database()

    def __getstate__(self):
        odict = self.__dict__.copy()
        del odict['logger']
        return odict

    def __setstate__(self, dict):
        logger = logging.getLogger()
        self.__dict__.update(dict)
        self.logger = logger

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
