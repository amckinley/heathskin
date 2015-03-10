from collections import defaultdict
import copy
import json
import operator
import logging

from heathskin import utils

CARD_DATA_PATH = "data/AllSets.json"

def deck_from_file(path):
    with open(path) as f:
        card_names = [n.rstrip() for n in f.readlines()]

    return Deck(card_names)

class Deck(object):
    def __init__(self, card_list):
        self.logger = logging.getLogger()
        if len(card_list) != 30:
            raise Exception("you must have exactly 30 cards; found {}".format(len(card_list)))

        self.read_card_data()
        self.card_list = card_list

        valid_cards = self.get_all_valid_names()
        for c in self.card_list:
            if c not in valid_cards:
                raise Exception("card is not valid: {}".format(c))


        #self.get_real_set_names()
        #print self.card_data.keys()
        self.get_taunters()

    def read_card_data(self):
        with open(CARD_DATA_PATH) as f:
            raw = json.load(f)
            self.card_data = {n: d for n, d in raw.items() if n in self.get_real_set_names()}

    def get_real_set_names(self):
        names = [
            "Basic",
            "Classic",
            #"Credits",
            "Curse of Naxxramas",
            #"Debug",
            "Goblins vs Gnomes",
            #"Missions",
            "Promotion",
            "Reward"]
            #"System"]
        return names

        print len(self.card_data.items())

        for n in names:
            card_set = self.card_data[n]
            print n, len(card_set)
            for c in card_set:
                print c['name']

            print

    def get_taunters(self):
        name_check = defaultdict(list)
        taunters = list()
        for set_name, card_set in self.card_data.items():
            for c in card_set:
                name_check[c['name']].append(c)


        for name, cards in name_check.items():
            if len(cards) == 1:
                continue

            differ = utils.MultiDictDiffer(cards)
            print "[{}] {}".format(name, len(cards))
            differ.get_diff()
            print
            # for k in changed:
            #     print "{} [{}] - [{}]".format(k, cards[0][k], cards[1][k])

            # print

                #[c['id'] for c in cards]

        #         if 'mechanics' in c and "Taunt" in c['mechanics']:
        #             taunters.append(c)

        # for c in taunters:
        #     print c['name'], c['id']

    def get_all_valid_names(self):
        valid_names = set()
        for set_name, card_set in self.card_data.items():
            for c in card_set:
                valid_names.add(c["name"])

        return valid_names

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
