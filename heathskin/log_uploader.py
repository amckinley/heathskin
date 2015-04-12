import logging
import requests
from heathskin.exceptions import UploaderException


class LogUploader(object):
    def __init__(self, log_server, username, password):
        self.logger = logging.getLogger()
        self.log_server = log_server
        self.username = username
        self.password = password
        self.log_url = "http://{}/upload_line".format(self.log_server)
        self.login_url = "http://{}/login".format(self.log_server)
        self.start_session_url = "http://{}/start_session".format(
            self.log_server)
        self.started = False
        self._line_count = 0

    def start(self):
        self._create_authenticated_session()
        self.started = True

    def upload_line(self, line):
        if not self.started:
            raise UploaderException("Must start uploader first")

        res = self.session.post(
            self.log_url,
            headers={'Authentication-Token': self.authentication_token},
            json={"log_line": line})

        res.raise_for_status()

        self._line_count += 1

    @property
    def line_count(self):
        return self._line_count

    def _create_authenticated_session(self):
        self.session = requests.Session()

        # authenticate ourselves and save the resulting auth token
        res = self.session.post(
            self.login_url,
            json={"email": self.username, "password": self.password})
        json_res = res.json()

        # first check the http status
        res.raise_for_status()

        # then check the meta status
        meta_status_code = json_res["meta"]["code"]
        if meta_status_code != 200:
            raise UploaderException("Failed to login: {}".format(
                json_res["response"]["errors"].values()[0][0]))


        self.authentication_token = json_res["response"]["user"]["authentication_token"]

        # begin the logging session
        res = self.session.post(
            self.start_session_url,
            headers={'Authentication-Token': self.authentication_token})

        res.raise_for_status()


if __name__ == '__main__':
    l = LogUploader("127.0.0.1:3000", "bearontheroof@gmail.com", "wangwang")
    l.upload_line("this is a line")
    l.upload_line("another line")
