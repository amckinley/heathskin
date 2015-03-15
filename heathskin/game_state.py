import re
import logging
from collections import defaultdict

from log_parser import LogParser
from entity import Entity

class GameState(object):
    def __init__(self, friendly_user_name=None, friendly_deck=None):
        self.entities = {}
        self.friendly_user_name = friendly_user_name
        self.friendly_deck = friendly_deck
        self.logger = logging.getLogger()
        self.parser = LogParser(self)


    def feed_line(self, line):
        pattern = "\[(?P<logger_name>\S+)\] (?P<log_source>\S+\(\)) - (?P<log_msg>.*)"
        results = re.match(pattern, line)
        if not results:
            return

        self.parser.feed_line(**results.groupdict())

        fr_hand = self.get_entity_counts_by_zone()
        if fr_hand:
            # self.logger.info("friendly hand: %s", self.get_friendly_hand())
            self.logger.info("entities in zones: %s", self.get_entity_counts_by_zone())

    def convert_log_zone(self, log_zone):
        if not log_zone:
            return log_zone
        log_zone = "".join([c for c in log_zone.lower() if c not in ["(", ")"]])

        result = "_".join(log_zone.split(" "))
        return result

    # XXX: stupid hack. the logs refer to the player entities by username
    def get_entity_by_name(self, ent_id):
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

        return self.entities[result_id]


    def get_friendly_hand(self):
        results = []
        for ent in self.entities.values():
            zone = ent.tags.get("ZONE", None)
            if zone == "FRIENDLY HAND":
                #self.logger.info(ent.tags)
                results.append(ent.card_id)

        return results


    def get_entity_counts_by_zone(self):
        results = defaultdict(int)
        for ent in self.entities.values():
            zone = ent.tags.get("ZONE", None)
            results[zone] += 1
        # {"zone": "entity id"}
        return results
