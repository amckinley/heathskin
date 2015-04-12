import os
import logging
import json
import dateutil.parser
from datetime import datetime
import codecs

from heathskin import game_state

class GameUniverse(object):
    def __init__(self, session_log_path):
        self.logger = logging.getLogger()
        self.session_log_path = session_log_path
        self.sessions = {}

    def get_session_log_path(self, user_id, session_start):
        return os.path.join(self.session_log_path, user_id, session_start.replace(":", "_"))

    def feed_line(self, user_id, session_start, log_line):
        session_key = (user_id, session_start)
        if session_key not in self.sessions:
            self.logger.info("Starting new session: %s", session_key)

            session_log_path = self.get_session_log_path(user_id, session_start)
            session_log_dir = os.path.dirname(session_log_path)
            if not os.path.exists(session_log_dir):
                os.makedirs(session_log_dir)

            file_handle = codecs.open(session_log_path, encoding='utf-8', mode='a')

            self.sessions[session_key] = {
                'last_seen_at': datetime.now(),
                'file_handle': file_handle,
                'game_state': game_state.GameState()
            }

        session = self.sessions[session_key]

        try:
            session['game_state'].feed_line(log_line.rstrip())
        except Exception as e:
            self.logger.error("Failed to update GameState with line: '%s", log_line.rstrip())
        session['last_seen_at'] = datetime.now()
        session['file_handle'].write(log_line)

    def get_game_state(self, user_id, session_start):
        session_key = (user_id, session_start)
        if session_key not in self.sessions:
            return None

        return self.sessions[session_key]['game_state']

    def get_latest_game_state_for_user(self, user_id):
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
        self.logger.info("Found a total of %d sessions for user %d, using %s",
            len(candidate_sessions), user_id, latest_session_start)

        session_key = (user_id, latest_session_start)
        return self.sessions[session_key]['game_state']

