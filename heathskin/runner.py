from game_state import GameState

def main():
    gs = GameState()
    f = open("/Users/rhigdon/Library/Logs/Unity/Player.log", "r")
    for line in f.readlines():
        gs.feed_line(line.rstrip())
        
if __name__ == "__main__":
    main()
