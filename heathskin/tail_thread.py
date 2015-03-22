import threading
import logging
import subprocess


class TailThread(threading.Thread):
    def __init__(self, hs_log_path, stop_flag, queue):
        threading.Thread.__init__(self)
        self.daemon = False

        self.logger = logging.getLogger()
        self.hs_log_path = hs_log_path
        self.queue = queue
        self.stop_flag = stop_flag

        self.process = None

    def run(self):
        self.logger.info("Starting log tailer at path %s", self.hs_log_path)
        self.process = subprocess.Popen(
            ["tail", "-f", "-c", "0", self.hs_log_path], stdout=subprocess.PIPE)

        try:
            while True:
                if self.stop_flag.is_set():
                    self.shutdown()
                    return

                self.poll_for_output()

        except Exception, e:
            self.logger.exception(e)
            self.shutdown()

    def poll_for_output(self):
        line = self.process.stdout.readline()

        if len(line) > 3 and not line.startswith('('):
            self.queue.put(line)

    def shutdown(self):
        self.logger.info("Shutting down log tailer...")
        self.process.kill()
        self.process.wait()
        self.logger.info("Log tailer shutdown")