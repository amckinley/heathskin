import logging
import requests
import json

class LogUploader(object):
    def __init__(self, log_server, username, password):
        self.logger = logging.getLogger()
        self.log_server = log_server
        self.username = username
        self.password = password
        self.log_url = "http://{}/upload_line".format(self.log_server)
        self.login_url = "http://{}/login".format(self.log_server)
        self.start_session_url = "http://{}/start_session".format(self.log_server)

        self._create_authenticated_session()

    def upload_line(self, line):
        res = self.session.post(
            self.log_url,
            headers={'Authentication-Token': self.authentication_token},
            json={"log_line": line})
        res.raise_for_status()

    def _create_authenticated_session(self):
        self.session = requests.Session()

        # authenticate ourselves and save the resulting auth token
        res = self.session.post(self.login_url, json={"email": self.username, "password": self.password})
        self.authentication_token = res.json()["response"]["user"]["authentication_token"]

        # begin the logging session
        self.session.post(
            self.start_session_url,
            headers={'Authentication-Token': self.authentication_token})

if __name__ == '__main__':
    l = LogUploader("127.0.0.1:3000", "bearontheroof@gmail.com", "wangwang")
    l.upload_line("this is a line")
    l.upload_line("another line")