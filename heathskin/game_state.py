import re
import logging
from collections import defaultdict
from datetime import datetime


from flask.ext.login import current_user


from heathskin.frontend import db
from heathskin.exceptions import PreventableException
from heathskin import card_database
from heathskin.models import GameHistory
from log_parser import LogParser


class GameState(object):
    @classmethod
    def build_from_entities(cls, entities):
        gs = GameState()
        gs.entities = entities
        return gs

    def __init__(self, friendy_player_name, replay_from_log=False):
        self.logger = logging.getLogger()
        self.replay_from_log = replay_from_log
        self.friendy_player_name = friendy_player_name

        self.players = {}

        self.start_new_game()
        self.game_type = None

        self.card_db = card_database.CardDatabase.get_database()

    def _create_history(self):
        """ Create Game History after game Ends
        """
        history = GameHistory()
        history.won = self.get_friendly_did_win()
        history.end_time = datetime.now()

        if current_user:
            history.user_id = current_user.get_id()
        else:
            history.user_id = 0

        history.hero = self.get_friendly_hero().name
        history.opponent = self.get_opposing_hero().name
        history.enemy_health, history.hero_health = self._get_hero_healths()
        history.turns = self.get_num_turns()

        history.first = not self.get_friendly_player_did_act_first()
        history.start_time = self.start_time
        for player in self.players.values():
            if player.get('first'):
                history.player1 = player.get('username')
            else:
                history.player2 = player.get('username')

        db.session.add(history)
        db.session.commit()

    def get_friendly_player(self):
        friend_ent, opposing_ent = self._get_player_entities()
        return friend_ent

    def get_opposing_player(self):
        friend_ent, opposing_ent = self._get_player_entities()
        return opposing_ent

    def _get_player_entities(self):
        if len(self.players) != 2:
            raise PreventableException("unknown players")

        friend_ent = None
        opposing_ent = None
        for k, v in self.players.items():
            if v['username'] == self.friendy_player_name:
                friend_ent = self.entities[v['entity_id']]
            else:
                opposing_ent = self.entities[v['entity_id']]

        return friend_ent, opposing_ent

    def get_friendly_hero(self):
        friend_hero, opposing_hero = self._get_hero_entities()
        return friend_hero

    def get_opposing_hero(self):
        friend_hero, opposing_hero = self._get_hero_entities()
        return opposing_hero

    def _get_hero_entities(self):
        friend_ent, opposing_ent = self._get_player_entities()
        friend_hero = self.entities.get(
            str(friend_ent.get_tag('HERO_ENTITY')))
        opposing_hero = self.entities.get(
            str(opposing_ent.get_tag('HERO_ENTITY')))

        return friend_hero, opposing_hero

    def get_friendly_health(self):
        friendly_health, opposing_health = self._get_hero_healths()
        return friendly_health

    def get_opposing_health(self):
        friendly_health, opposing_health = self._get_hero_healths()
        return opposing_health

    def _get_hero_healths(self):
        friendly_hero, opposing_hero = self._get_hero_entities()
        friendly_health = (30 - friendly_hero.get_tag('DAMAGE', 0))
        opposing_health = (30 - opposing_hero.get_tag('DAMAGE', 0))

        return friendly_health, opposing_health

    def get_friendly_player_did_act_first(self):
        if len(self.players) != 2:
            raise PreventableException("huge fuckup")

        friendly = self.get_friendly_player()
        return friendly.get_tag("FIRST_PLAYER") == 1

    def get_friendly_did_win(self):
        play_state = self.get_friendly_player().get_tag('PLAYSTATE')

        if play_state == "WON":
            return True
        elif play_state == "LOST":
            return False
        else:
            raise PreventableException(
                "winner isnt known?! '{}'".format(play_state))

    def set_game_type(self, new_game_type):
        self.game_type = new_game_type
        self.logger.info("New game type detected: %s", self.game_type)

    def feed_line(self, line):
        bob_pattern = "\[Bob\] ---(?P<log_msg>.*)---"
        bob_results = re.match(bob_pattern, line)

        if bob_results:
            results = bob_results.groupdict()
            self.parser.feed_line("Bob", "BobLog", results["log_msg"])

        else:
            pattern = "\[(?P<logger_name>\S+)\] (?P<log_source>\S+\(\)) - (?P<log_msg>.*)"  # noqa
            results = re.match(pattern, line)

            if not results:
                return

            self.parser.feed_line(**results.groupdict())

        if self.is_gameover() and not self.replay_from_log:
            our_hero, enemy_hero = self._get_hero_entities()

            self._create_history()
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
        self.start_time = datetime.now()

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

        result = self.entities.get(result_id, default)
        return result

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

    def get_friendly_played_cards(self):
        return self._get_played_cards("FRIENDLY")

    def _get_played_cards(self, player):
        played_cards = []
        zones = ["HAND", "PLAY", "GRAVEYARD", "SECRET"]
        for zone in zones:
            played_cards += self.get_entities_by_zone(player + " " + zone)
        return played_cards

    def get_num_turns(self):
        return self.entities.get('1').get_tag('TURN')
