import unittest2

from heathskin import card_database
from utils import replayer


class TestLogParser(unittest2.TestCase):
    def setUp(self):
        self.gs = replayer("tests/logs/simple_concede.log")
        self.card_db = card_database.CardDatabase.get_database()

    def test_simple_concede(self):
        friendly_player = self.gs.get_friendly_player()
        friendly_hero = self.gs.get_friendly_hero()
        friendly_hero_name = self.card_db.get_card_by_id(
            friendly_hero.card_id)['name']

        opposing_player = self.gs.get_opposing_player()
        opposing_hero = self.gs.get_opposing_hero()

        opposing_hero_name = self.card_db.get_card_by_id(
            opposing_hero.card_id)['name']

        print friendly_hero.card_id
        self.assertEqual(opposing_hero_name, "Jaina Proudmoore")
        self.assertEqual(friendly_hero_name, "Rexxar")

        friendly_health = self.gs.get_friendly_health()
        opposing_health = self.gs.get_opposing_health()
        self.assertEqual(friendly_health, 27)
        self.assertEqual(opposing_health, 26)