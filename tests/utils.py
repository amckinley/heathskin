
import logging
from sys import exit


from iso8601 import iso8601


from heathskin.frontend import app, db  # noqa
from heathskin.game_state import GameState


def iso_str_to_datetime(iso_str):
    return iso8601.parse_date(iso_str)


def replayer(path, player):
    logger = logging.getLogger()
    gs = GameState(friendy_player_name=player, replay_from_log=True)
    f = open(path, "r")

    for line in f.readlines():

        try:
            time_stamp, log_msg = line.split("\t", 1)
        except ValueError:
            logger.error("failed to find timestamp in log file. did you mean to use a v1 log file?")  # noqa
            exit(-1)

        gs.feed_line(log_msg.rstrip())

    return gs
