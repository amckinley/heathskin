import re
import logging
from collections import defaultdict
import json
from heathskin.frontend import db
from models import GameHistory
from flask.ext.login import current_user

from log_parser import LogParser
from entity import Entity

class GameState(object):
    @classmethod
    def build_from_entities(cls, entities):
        gs = GameState()
        gs.entities = entities
        return gs

    def __init__(self, friendly_user_name=None):
        self.friendly_user_name = friendly_user_name
        self.logger = logging.getLogger()

        self.start_new_game()

    def __getstate__(self):
        odict = self.__dict__.copy()
        del odict['logger']
        return odict

    def __setstate__(self, dict):
        logger = logging.getLogger()
        self.__dict__.update(dict)
        self.logger = logger

    def feed_line(self, line):
        pattern = "\[(?P<logger_name>\S+)\] (?P<log_source>\S+\(\)) - (?P<log_msg>.*)"
        results = re.match(pattern, line)
        if not results:
            return

        self.parser.feed_line(**results.groupdict())

        if self.is_gameover():
            #print 'game over %s' % self.entities[4].name
            history = GameHistory()
            history.user_id = current_user.get_id()
            db.session.add(history)
            db.session.commit()
            self.logger.info("Detected gameover")
            self.start_new_game()

    def convert_log_zone(self, log_zone):
        if not log_zone:
            return log_zone
        log_zone = "".join([c for c in log_zone.lower() if c not in ["(", ")"]])

        result = "_".join(log_zone.split(" "))
        return result

    def is_gameover(self):
        game_ent = self.get_entity_by_name("GameEntity", None)
        return game_ent and game_ent.get_tag("STATE") == "COMPLETE"

    def start_new_game(self):
        self.logger.info("Starting new game")
        self.entities = {}
        self.parser = LogParser(self)

    # XXX: stupid hack. the logs refer to the player entities by username
    def get_entity_by_name(self, ent_id, default=None):
        result_id = None
        try:
            int(ent_id)
            result_id = ent_id
        except ValueError:
            if ent_id == "GameEntity":
                result_id = "1"
            elif ent_id == self.friendly_user_name:
                result_id = "2"
            else:
                result_id = "3"

        return self.entities.get(result_id, default)

    def get_entities_by_zone(self, zone):
        return [ent for ent in self.entities.values() if ent.get_tag("ZONE") == zone]

    def get_friendly_hand(self):
        return self.get_entities_by_zone("FRIENDLY HAND")

    def get_opposing_hand(self):
        return self.get_entities_by_zone("OPPOSING HAND")

    def get_entity_counts_by_zone(self):
        results = defaultdict(int)
        for ent in self.entities.values():
            zone = ent.tags.get("ZONE", None)
            results[zone] += 1
        return results

    def get_played_cards(self, player):
        played_cards = []
        # HAND
        played_cards += self.get_entities_by_zone("{} HAND".format(player))
        # PLAY
        played_cards += self.get_entities_by_zone("{} PLAY".format(player))
        # GRAVEYARD
        played_cards + self.get_entities_by_zone("{} GRAVEYARD".format(player))

        return played_cards

    def get_all_zone_names():
        pass
