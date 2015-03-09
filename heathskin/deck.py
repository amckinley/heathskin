from collections import defaultdict
import copy
import json
import operator

CARD_DATA_PATH = "data/AllSets.json"

def deck_from_file(path):
    with open(path) as f:
        card_names = [n.rstrip() for n in f.readlines()]

    return Deck(card_names)

class Deck(object):
    def __init__(self, card_list):
        if len(card_list) != 30:
            raise Exception("you must have exactly 30 cards; found {}".format(len(card_list)))

        self.card_list = card_list

        valid_cards = self.get_all_valid_names()
        for c in self.card_list:
            if c not in valid_cards:
                raise Exception("card is not valid: {}".format(c))

    def get_all_valid_names(self):
        with open(CARD_DATA_PATH) as f:
            card_data = json.load(f)

        valid_names = set()
        for set_name, card_set in card_data.items():
            print set_name
            for c in card_set:
                valid_names.add(c["name"])

        return valid_names

    def consume_card_by_name(self, card_name):
        if card_name in self.in_deck:
            print "consuming card", card_name
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
