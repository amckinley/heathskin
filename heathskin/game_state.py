import re
import logging
from collections import defaultdict
from exceptions import PreventableException
from heathskin.frontend import db
from heathskin.exceptions import PreventableException
from heathskin import card_database
from heathskin.models import GameHistory
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
        self.players = {}

    def _create_history(self, *args, **kwargs):
        """ Create Game History after game Ends
        """
        history = GameHistory()
        history.won = self._get_first_player_entity().get_tag('PLAYSTATE') == "WON"
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
        for player in self.players.values():
          if player.get('first'):
            history.player1 = player.get('username')
          else:
            history.player2 = player.get('username')
        db.session.add(history)
        db.session.commit()

    def _get_entity_id_of_first_player(self):
        for player in self.players.values():
          if player.get('first'):
            return player.get('entity_id')

    def _get_first_player_entity(self):
        return self.entities.get(self._get_entity_id_of_first_player())

    def _get_first_hero_entity(self):
        first_player = self._get_first_player_entity()
        return self.entities.get(str(first_player.get_tag('HERO_ENTITY')))

    def _get_entity_id_of_second_player(self):
        for player in self.players.values():
          if not player.get('first'):
            return player.get('entity_id')

    def _get_second_hero_entity(self):
        second_player = self.entities.get(self._get_entity_id_of_second_player())
        return self.entities.get(str(second_player.get_tag('HERO_ENTITY')))

    def _get_heroes_from_entities(self):
        """ Find both heroes from the entities dictionary
          The Hero can randomly be in position 4 or 36
        """
        return self._get_first_hero_entity(), self._get_second_hero_entity()

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
        self.players = {}

    def get_entity_by_name(self, ent_id, default=None):
        result_id = None
        try:
            int(ent_id)
            result_id = ent_id
        except ValueError:
            if ent_id == "GameEntity":
                result_id = "1"
            else:
                raise PreventableException(
                    'failed to get entity by name : ' + ent_id)

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
