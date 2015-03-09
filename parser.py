import threading
import Queue
import subprocess
import time
import argparse

from game_state import GameState
import deck

LOG_PATH = "/Users/amckinley/Library/Logs/Unity/Player.log"

my_log_path = "./game_log.txt"


class TailThread(threading.Thread):
    def __init__(self, stop_flag, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.stop_flag = stop_flag
        self.daemon = False

        self.process = subprocess.Popen(["tail", "-f", LOG_PATH], stdout=subprocess.PIPE)
 
 
    def run(self):
        print "starting tailer thread"
        
        try:
            while True:
                if self.stop_flag.is_set():
                    self.shutdown()
                    return

                self.poll_for_output()

        except Exception as e:
            print "crashing on", e
            self.shutdown()

    def poll_for_output(self):
        line = self.process.stdout.readline()
 
        if len(line) > 3 and not line.startswith('('):
            self.queue.put(line)

    def shutdown(self):
        print "shutting down tailer thread"
        self.process.kill()
        self.process.wait()
        print "child process killed"



def run(args):
    
    #t = threading.Thread(target=tail_forever, args=(LOG_PATH,)).start()
    
    my_log = open(my_log_path, "w")
    d = deck.deck_from_file("rage_mage.deck")
    gs = GameState(friendly_deck=d)
    
    # noop

    def shutdown():
        stopper.set()
        print "set the event"
        t.join()


    try:
        if args.dev:
            fake_lines = open("trans_log2.txt")
            for l in fake_lines.readlines():
                gs.feed_line(l.rstrip())
            print "done with fake data"
            return


        stopper = threading.Event()
        output_queue = Queue.Queue(maxsize=10) # buffer at most 100 lines
        t = TailThread(stopper, output_queue)
        t.start()

        while True:
            try:
                line = output_queue.get_nowait()
            except Queue.Empty:
                continue

            #line = output_queue.get() # blocks
            my_log.write(line)
            

            if "m_currentTaskList" in line:
                continue

            if "TRANSITIONING" not in line:
                continue

            # trans_log.write(line)
            gs.feed_line(line.rstrip()) 
            #print tailq.get_nowait() # throws Queue.Empty if there are no lines to read
    except KeyboardInterrupt:
        print "got ctrl c"
        shutdown()


def main(args):
    run(args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--dev', action="store_true", default=False,
            help='sum the integers (default: find the max)')
    args = parser.parse_args()

    main(args)