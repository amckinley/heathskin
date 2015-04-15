import os
import logging
import dateutil.parser
from datetime import datetime
import codecs

from heathskin import game_state

SESSION_LOG_ROOT = "session_logs"


class GameUniverse(object):
    _instance = None

    @classmethod
    def get_universe(cls, session_log_path=None):
        if not cls._instance:
            cls._instance = GameUniverse(session_log_path)

        return cls._instance

    def __init__(self, session_log_path=None):
        self.logger = logging.getLogger()
        if not session_log_path:
            session_log_path = SESSION_LOG_ROOT
        self.session_log_path = session_log_path
        self.sessions = {}

    def get_session_dump(self):
        results = {}
        for k, v in self.sessions.items():
            results[str(k)] = v

        return results

    def get_session_log_path(self, user_id, session_start):
        return os.path.join(
            self.session_log_path, user_id, session_start.replace(":", "_"))

    def feed_line(self, user_id, session_start, log_line):
        session_key = (int(user_id), session_start)
        if session_key not in self.sessions:
            self.logger.info("Starting new session: %s", session_key)

            session_log_path = self.get_session_log_path(
                user_id, session_start)
            session_log_dir = os.path.dirname(session_log_path)
            if not os.path.exists(session_log_dir):
                os.makedirs(session_log_dir)

            file_handle = codecs.open(
                session_log_path, encoding='utf-8', mode='a')

            self.sessions[session_key] = {
                'last_seen_at': datetime.now(),
                'file_handle': file_handle,
                'game_state': game_state.GameState(),
                'lines_seen': 0
            }

        session = self.sessions[session_key]

        try:
            session['game_state'].feed_line(log_line.rstrip())
        except Exception as e:
            print "Failed to update GameState with line: '%s" % log_line.rstrip()
            print dir(e)
            print e.__class__
            print e.message
        session['last_seen_at'] = datetime.now()
        session['file_handle'].write(log_line)
        session['lines_seen'] += 1

    def get_game_state(self, user_id, session_start):
        session_key = (user_id, session_start)
        if session_key not in self.sessions:
            return None

        return self.sessions[session_key]['game_state']

    def get_latest_game_state_for_user(self, user_id):
        session_key = self.get_latest_session_for_user(user_id)
        if session_key not in self.sessions:
            return None

        return self.sessions[session_key]['game_state']

    def get_latest_session_for_user(self, user_id):
        user_id = int(user_id)
        candidate_sessions = []
        candidate_reverse_map = {}

        for uid, s_start in self.sessions.keys():
            if uid == user_id:
                date_obj = dateutil.parser.parse(s_start)
                candidate_sessions.append(date_obj)
                candidate_reverse_map[date_obj] = s_start
        if not candidate_sessions:
            return None

        cs = sorted(candidate_sessions)
        latest_session_start = candidate_reverse_map[cs[-1]]
        self.logger.info(
            "Found a total of %d sessions for user %d, using %s",
            len(candidate_sessions), user_id, latest_session_start)

        session_key = (user_id, latest_session_start)
        return session_key
