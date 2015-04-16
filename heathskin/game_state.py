import re
import logging
from collections import defaultdict
from exceptions import PreventableException
from heathskin.frontend import db
from heathskin import card_database
from models import GameHistory
from flask.ext.login import current_user


from log_parser import LogParser


class GameState(object):
    @classmethod
    def build_from_entities(cls, entities):
        gs = GameState()
        gs.entities = entities
        return gs

    def __init__(self):
        self.logger = logging.getLogger()
        self.start_new_game()
        self.player1 = None
        self.player2 = None

    def _create_history(self, *args, **kwargs):
        """ Create Game History after game Ends
        """
        history = GameHistory()
        history.won = self.player.get_tag('PLAYSTATE') == "WON"
        if current_user:
            history.user_id = current_user.get_id()
        else:
            history.user_id = 0
        history.hero = kwargs.get('hero')
        history.opponent = kwargs.get('opponent')
        history.enemy_health = 30
        history.hero_health = 30
        history.turns = kwargs.get('turns')
        history.first = not self._is_player_first()
        if self.player1:
            history.player1 = self.player1
        if self.player2:
            history.player2 = self.player2
        db.session.add(history)
        db.session.commit()

    def _get_heroes_from_entities(self):
        """ Find both heroes from the entities dictionary
          The Hero can randomly be in position 4 or 36
        """
        entity2 = self.entities.get('2')
        entity3 = self.entities.get('3')
        our_hero = self.entities.get('4')
        second_pos = self.entities.get('3').get_tag('HERO_ENTITY')
        enemy_hero = self.entities.get(str(second_pos))
        if our_hero.get_tag('ZONE') == 'OPPOSING PLAY (Hero)':
            enemy_hero = our_hero
            our_hero = self.entities.get(str(second_pos))
            self.player = entity2 if self._is_player_first() else entity3
        else:
            self.player = entity3 if self._is_player_first() else entity2
        return our_hero, enemy_hero

    def _is_player_first(self):
        return self.entities.get('36').get_tag('ZONE') == 'OPPOSING PLAY (Hero)'

    def feed_line(self, line):
        pattern = "\[(?P<logger_name>\S+)\] (?P<log_source>\S+\(\)) - (?P<log_msg>.*)"  # noqa
        results = re.match(pattern, line)
        if not results:
            return

        self.parser.feed_line(**results.groupdict())

        if self.is_gameover():
            card_db = card_database.CardDatabase.get_database()
            our_hero, enemy_hero = self._get_heroes_from_entities()
            self._create_history(**{
                'hero': card_db.get_card_by_id(our_hero.card_id)['name'],
                'opponent': card_db.get_card_by_id(enemy_hero.card_id)['name'],
                'turns': self.entities.get('1').get_tag('TURN'),
            })
            self.logger.info("Detected gameover")
            self.start_new_game()

    def convert_log_zone(self, log_zone):
        if not log_zone:
            return log_zone
        log_zone = "".join(
            [c for c in log_zone.lower() if c not in ["(", ")"]])

        result = "_".join(log_zone.split(" "))
        return result

    def is_gameover(self):
        game_ent = self.get_entity_by_name("GameEntity", None)
        return game_ent and game_ent.get_tag("STATE") == "COMPLETE"

    def start_new_game(self):
        self.logger.info("Starting new game")
        self.entities = {}
        self.parser = LogParser(self)
        self.player1 = None
        self.player2 = None

    # XXX: stupid hack. the logs refer to the player entities by username
    def get_entity_by_name(self, ent_id, default=None):
        result_id = None
        try:
            int(ent_id)
            result_id = ent_id
        except ValueError:
            if ent_id == "GameEntity":
                result_id = "1"
            elif ent_id == self.player1:
                result_id = "2" if self._is_player_first() else "3"
            elif ent_id == self.player2:
                result_id = "3" if self._is_player_first() else "2"
            else:
                raise PreventableException('failed to get entity by name : ' +  ent_id)

        return self.entities.get(result_id, default)

    def get_entities_by_zone(self, zone):
        return [
            ent for ent
            in self.entities.values() if ent.get_tag("ZONE") == zone]

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
