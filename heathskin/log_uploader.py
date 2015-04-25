import logging
import requests
from heathskin.exceptions import UploaderException


class LogUploader(object):
    def __init__(self, log_server, username, password):
        self.logger = logging.getLogger()
        self.log_server = log_server
        self.username = username
        self.password = password
        self.log_url = "http://{}/upload_lines".format(self.log_server)
        self.login_url = "http://{}/login".format(self.log_server)
        self.start_session_url = "http://{}/start_session".format(
            self.log_server)
        self.started = False
        self._uploaded_count = 0
        self._skipped_count = 0

    def start(self):
        self._create_authenticated_session()
        self.started = True

    def upload_lines(self, lines):
        if not self.started:
            raise UploaderException("Must start uploader first")

        clean_lines = [l for l in lines if self._check_line(l)]

        res = self.session.post(
            self.log_url,
            headers={'Authentication-Token': self.authentication_token},
            json={"log_lines": clean_lines})

        res.raise_for_status()

        self._uploaded_count += len(clean_lines)
        self._skipped_count += len(lines) - len(clean_lines)

    def _check_line(self, line):
        # discard the Unity log source lines
        if line.startswith("(Filename:"):
            return False

        # discard lines with nothing but whitespace
        if not line.rstrip():
            return False

        return True

    @property
    def uploaded_count(self):
        return self._uploaded_count

    @property
    def skipped_count(self):
        return self._skipped_count

    def _create_authenticated_session(self):
        self.session = requests.Session()

        # authenticate ourselves and save the resulting auth token
        res = self.session.post(
            self.login_url,
            json={"email": self.username, "password": self.password})

        try:
            json_res = res.json()
        except ValueError:
            raise UploaderException("No JSON in response: {}".format(res.text))

        # first check the http status
        res.raise_for_status()

        # then check the meta status
        meta_status_code = json_res["meta"]["code"]
        if meta_status_code != 200:
            raise UploaderException("Failed to login: {}".format(
                json_res["response"]["errors"].values()[0][0]))

        user = json_res["response"]["user"]
        self.authentication_token = user["authentication_token"]

        # begin the logging session
        res = self.session.post(
            self.start_session_url,
            headers={'Authentication-Token': self.authentication_token})

        res.raise_for_status()


if __name__ == '__main__':
    l = LogUploader("127.0.0.1:3000", "bearontheroof@gmail.com", "wangwang")
    l.upload_line("this is a line")
    l.upload_line("another line")
