import re
from collections import defaultdict

from utils import params_to_dict
from entity import Entity

class GameState(object):
    def __init__(self, friendly_deck=None):
        self.zones = defaultdict(dict)
        self.entities = {}
        self.friendly_deck = friendly_deck

    def feed_line(self, line):
        pattern = "\[(?P<logger_name>\S+)\] (?P<log_source>\S+) - (?P<action_type>.+) \[(?P<entity_data>.+?)\] to( (?P<dest_zone>.+)|)"
        results = re.match(pattern, line).groupdict()
        self.update_entity(results["entity_data"], results["dest_zone"])
        #self.print_current_state()

    def find_zone_for_entity(self, entity_id):
        for z_name, z_contents in self.zones.items():
            if entity_id in z_contents:
                return z_name

        return None

    def update_entity(self, entity_data, dest_zone):
        parsed_data = params_to_dict(entity_data)
        new_ent = Entity(**parsed_data)

        dest_zone = self.convert_log_zone(dest_zone)

        if new_ent.id in self.entities:
            old_zone = self.find_zone_for_entity(new_ent.id)
            if old_zone:
                del self.zones[old_zone][new_ent.id]

            #print "moving ent '{}' from zone '{}' to '{}'".format(new_ent, old_zone, dest_zone)
            old_ent = self.entities[parsed_data["id"]]
            if dest_zone:
                self.zones[dest_zone][new_ent.id] = new_ent
        else:
            #print "got a new entity with id {}, adding it to zone {}".format(new_ent.id, dest_zone)
            self.zones[dest_zone][new_ent.id] = new_ent

        # if dest_zone == "friendly_hand":
        print "current hand:", [e.name for e in self.zones['friendly_hand'].values()]
        self.friendly_deck.print_draw_probs(
                self.zones["friendly_deck"].values(),
                self.zones["friendly_hand"].values(),
                self.zones["friendly_play"].values(),
                self.zones["friendly_graveyard"].values(),
                )
        print

        self.entities[new_ent.id] = new_ent
        
        #print "created new ent, it looks like this:", new_ent

    def convert_log_zone(self, log_zone):
        if not log_zone:
            return log_zone
        log_zone = "".join([c for c in log_zone.lower() if c not in ["(", ")"]])
        
        result = "_".join(log_zone.split(" "))
        return result


    def print_current_state(self):
        for z_name, z_contents in self.zones.items():
            if z_name in ["opposing_deck", "friendly_deck"] or "hero" in z_name:
                continue
            
            contents = str(z_contents)

            print z_name, ":", contents
