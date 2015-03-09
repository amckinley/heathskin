from game_state import GameState

def main():
    gs = GameState()
    f = open("trans_log.txt", "r")
    for line in f.readlines():
        gs.feed_line(line.rstrip())
        
if __name__ == "__main__":
    main()