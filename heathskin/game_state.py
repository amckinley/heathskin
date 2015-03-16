import re
import logging
from collections import defaultdict
import requests
import json

from log_parser import LogParser
from entity import Entity

class GameState(object):
    def __init__(self, friendly_user_name=None, friendly_deck=None):
        self.friendly_user_name = friendly_user_name
        self.friendly_deck = friendly_deck
        self.logger = logging.getLogger()

        self.start_new_game()

    def feed_line(self, line):
        pattern = "\[(?P<logger_name>\S+)\] (?P<log_source>\S+\(\)) - (?P<log_msg>.*)"
        results = re.match(pattern, line)
        if not results:
            return

        self.parser.feed_line(**results.groupdict())

        # fr_hand = self.get_friendly_hand()
        # if fr_hand:
        #     # self.logger.info("friendly hand: %s", self.get_friendly_hand())
        #     self.logger.info("entities in zones: %s", self.get_entities_by_zone("FRIENDLY HAND"))


        data = {
            "entity_counts_by_zone": self.get_entity_counts_by_zone(),
            "friendly_hand": [ent.card_id for ent in self.get_friendly_hand()],
            "opposing_hand": [ent.card_id for ent in self.get_opposing_hand()]
        }

        target_url = "http://127.0.0.1:3000/update_state"
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(target_url, data=json.dumps(data), headers=headers)

        if self.is_gameover():
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
