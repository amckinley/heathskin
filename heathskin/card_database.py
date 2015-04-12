from collections import defaultdict
import json
import logging

from heathskin import utils

CARD_DATABASE_JSON_PATH = "data/AllSets.json"

logger = logging.getLogger()


class CardDatabase(object):
    _db_cache = {}

    @classmethod
    def get_database(cls, db_path=CARD_DATABASE_JSON_PATH):
        if db_path not in cls._db_cache:
            logger.info("Creating card database from path %s", db_path)
            cls._db_cache[db_path] = CardDatabase(db_path)

        return cls._db_cache[db_path]

    def __init__(self, database_path):
        self.database_path = database_path
        self.logger = logger

        self.read_card_data()

    def read_card_data(self):
        with open(self.database_path) as f:
            raw = json.load(f)
            self.card_data = {n: d for n, d in raw.items() if n in self.get_real_set_names()}

    def search(self, initial_cards=None, collectible=True, name=None,
            cost=None, card_type=None,
            rarity=None, faction=None, mechanics=None, attack=None, health=None,
            player_class=None):

        def _filter(cs, key, value):
            return [c for c in cs if key in c and c[key] == value]

        if initial_cards:
            cards_remaining = initial_cards
        else:
            cards_remaining = self.all_cards

        if collectible:
            cards_remaining = _filter(cards_remaining, 'collectible', True)

        if cost:
            cards_remaining = _filter(cards_remaining, 'cost', cost)

        if card_type:
            cards_remaining = _filter(cards_remaining, 'type', card_type)

        if rarity:
            cards_remaining = _filter(cards_remaining, 'rarity', rarity)

        if faction:
            cards_remaining = _filter(cards_remaining, 'faction', faction)

        if attack:
            cards_remaining = _filter(cards_remaining, 'attack', attack)

        if health:
            cards_remaining = _filter(cards_remaining, 'health', health)

        if player_class:
            cards_remaining = _filter(
                cards_remaining, 'playerClass', player_class)

        # substring match
        if name:
            cards_remaining = [c for c in cards_remaining if name in c['name']]

        # logical AND
        if mechanics:
            for m in mechanics:
                cards_remaining = [c for c in cards_remaining if 'mechanics' in c and m in c['mechanics']]

        return list(cards_remaining)

    @property
    def cards_by_id(self):
        ids = dict()
        for c in self.all_cards:
            if c['id'] in ids:
                raise Exception(
                    "lol, same id for two cards: '{}'".format(c['id']))

            ids[c['id']] = c

        return ids

    @property
    def all_cards(self):
        for n, card_set in self.card_data.items():
            for c in card_set:
                yield c

    @property
    def cards_by_mechanic(self):
        mechs = defaultdict(list)
        for c in self.all_cards:
            if 'mechanics' in c:
                for m in c['mechanics']:
                    mechs[m].append(c)

        return mechs

    @property
    def all_collectible_cards(self):
        collectible = list()
        for c in self.all_cards:
            if 'collectible' in c and c['collectible']:
                collectible.append(c)

        return collectible

    def get_card_by_id(self, card_id):
        return self.cards_by_id[card_id]

    def get_real_set_names(self):
        names = [
            "Basic",
            "Classic",
            #"Credits",
            "Curse of Naxxramas",
            #"Debug",
            "Goblins vs Gnomes",
            "Blackrock Mountain",
            #"Missions",
            "Promotion",
            "Reward"]
            #"System"]
        return names

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

            flavor_flavs = [c.get('flavor', None) for c in cards]

            found_flav = False
            for f in flavor_flavs:
                if f is not None:
                    if found_flav:
                        print "OH NOOOOO", flavor_flavs
                        return
                    else:
                        found_flav = True
                        print "flavor resolved!"
                        break

            if not found_flav:
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
