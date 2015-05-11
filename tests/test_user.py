import unittest2

from heathskin import card_database, models
from utils import replayer

class TestUser(unittest2.TestCase):

    def test_get_log_name(self):
        andrew = models.User.query.filter_by(id=2).first()
        print andrew
        self.assertEqual(andrew.get_log_name(), "And0r")
