import re
import logging
from collections import defaultdict
import json
from heathskin.frontend import db
from heathskin import card_database
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

    def _create_history(self, *args, **kwargs):
        player = self.entities.get('3')
        if not player.get_tag('CARDTYPE') == 'PLAYER':
          player = self.entities.get('2')
        history = GameHistory()
        history.won = player.get_tag('PLAYSTATE') == "WON"
        history.user_id = current_user.get_id()
        history.hero = kwargs.get('hero')
        history.opponent = kwargs.get('opponent')
        history.enemy_health = 30 - int(player.get_tag('DAMAGE'))
        history.hero_health = kwargs.get('hero_health')
        history.turns = kwargs.get('turns')
        db.session.add(history)
        db.session.commit()

    def feed_line(self, line):
        pattern = "\[(?P<logger_name>\S+)\] (?P<log_source>\S+\(\)) - (?P<log_msg>.*)"
        results = re.match(pattern, line)
        if not results:
            return

        self.parser.feed_line(**results.groupdict())

        if self.is_gameover():
            import ipdb
            ipdb.set_trace()
            #print ' 2 : %s' % self.entities.get('1').tags
            #print ' 2 : %s' % self.entities.get('3').tags
            for entity_id in self.entities:
              entity = self.entities[entity_id]
              print entity.tags
            card_db = card_database.CardDatabase.get_database()
            our_hero = self.entities.get('4')
            if not our_hero.get_tag('ZONE') == 'FRIENDLY PLAY (Hero)':
              enemy_hero = our_hero
            our_hero = self.entities.get('36')

            self._create_history(**{
              'hero': card_db.get_card_by_id(our_hero.card_id)['name'],
              'hero_health': our_hero.get_tag('HEALTH'),
              'opponent': card_db.get_card_by_id(enemy_hero.card_id)['name'],
              'enemy_health': enemy_hero.get_tag('HEALTH'),
              'turns': self.entities.get('1').get_tag('TURN'),
            })
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

    def get_played_cards_friendly(self):
        return self.get_played_cards("FRIENDLY")

    def get_played_cards(self, player):
        played_cards = []
        zones = ["HAND", "PLAY", "GRAVEYARD", "SECRET", "DECK"]
        for zone in zones:
            played_cards += self.get_entities_by_zone(player + " " + zone)
        return played_cards

    def get_all_zone_names():
        pass
