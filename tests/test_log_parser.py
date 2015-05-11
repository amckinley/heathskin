import unittest2

from heathskin import card_database
from utils import replayer


class TestSimpleConcede(unittest2.TestCase):
    def setUp(self):
        self.gs = replayer("tests/logs/simple_concede.log", "austin")
        self.card_db = card_database.CardDatabase.get_database()

    def test_simple_concede(self):
        friendly_player = self.gs.get_friendly_player()
        friendly_hero = self.gs.get_friendly_hero()

        opposing_player = self.gs.get_opposing_player()
        opposing_hero = self.gs.get_opposing_hero()

        self.assertEqual(opposing_hero.name, "Jaina Proudmoore")
        self.assertEqual(friendly_hero.name, "Rexxar")

        friendly_health = self.gs.get_friendly_health()
        opposing_health = self.gs.get_opposing_health()
        self.assertEqual(friendly_health, 27)
        self.assertEqual(opposing_health, 26)

        print self.gs.get_friendly_played_cards()
        print friendly_player.tags.items()

        self.assertEqual(self.gs.get_num_turns(), 3)

        self.assertEqual(self.gs.get_friendly_player_did_act_first(), True)
        self.gs._create_history()

class TestShortMage(unittest2.TestCase):
    def setUp(self):
        self.gs = replayer("tests/logs/shortmage.log", "And0r")
        self.card_db = card_database.CardDatabase.get_database()

    def test_short_mage(self):
        friendly_player = self.gs.get_friendly_player()
        friendly_hero = self.gs.get_friendly_hero()

        opposing_player = self.gs.get_opposing_player()
        opposing_hero = self.gs.get_opposing_hero()

        self.assertEqual(opposing_hero.name, "Malfurion Stormrage")
        self.assertEqual(friendly_hero.name, "Jaina Proudmoore")

        friendly_health = self.gs.get_friendly_health()
        opposing_health = self.gs.get_opposing_health()
        self.assertEqual(friendly_health, 30)
        self.assertEqual(opposing_health, 25)

        print self.gs.get_friendly_played_cards()
        print friendly_player.tags.items()

        self.assertEqual(self.gs.get_num_turns(), 3)

        self.assertEqual(self.gs.get_friendly_player_did_act_first(), True)
        self.gs._create_history()

    def test_played_cards(self):
        expected_blizz_ids = ["CS2_024", "NEW1_012"]
        actual_blizz_ids = [e.card_id for e in self.gs.get_friendly_played_cards()]

        self.assertEqual(actual_blizz_ids, expected_blizz_ids)
