"""
ACTION_START Entity=[name=Violet Apprentice id=71 zone=PLAY zonePos=3 cardId=NEW1_026t player=2] SubType=ATTACK Index=-1 Target=[name=Rexxar id=4 zone=PLAY zonePos=0 cardId=HERO_05 player=1]
    TAG_CHANGE Entity=GameEntity tag=PROPOSED_ATTACKER value=71
    TAG_CHANGE Entity=GameEntity tag=PROPOSED_DEFENDER value=4
    TAG_CHANGE Entity=[name=Violet Apprentice id=71 zone=PLAY zonePos=3 cardId=NEW1_026t player=2] tag=ATTACKING value=1
    TAG_CHANGE Entity=GameEntity tag=NEXT_STEP value=MAIN_ACTION
    TAG_CHANGE Entity=GameEntity tag=STEP value=MAIN_COMBAT
    TAG_CHANGE Entity=austin tag=NUM_OPTIONS_PLAYED_THIS_TURN value=1
    TAG_CHANGE Entity=[name=Rexxar id=4 zone=PLAY zonePos=0 cardId=HERO_05 player=1] tag=DEFENDING value=1
    TAG_CHANGE Entity=[name=Rexxar id=4 zone=PLAY zonePos=0 cardId=HERO_05 player=1] tag=PREDAMAGE value=1
    TAG_CHANGE Entity=[name=Rexxar id=4 zone=PLAY zonePos=0 cardId=HERO_05 player=1] tag=PREDAMAGE value=0
    META_DATA - Meta=META_DAMAGE Data=1 Info=1
    TAG_CHANGE Entity=[name=Rexxar id=4 zone=PLAY zonePos=0 cardId=HERO_05 player=1] tag=LAST_AFFECTED_BY value=71
    TAG_CHANGE Entity=[name=Rexxar id=4 zone=PLAY zonePos=0 cardId=HERO_05 player=1] tag=DAMAGE value=6
    TAG_CHANGE Entity=[name=Violet Apprentice id=71 zone=PLAY zonePos=3 cardId=NEW1_026t player=2] tag=NUM_ATTACKS_THIS_TURN value=1
    TAG_CHANGE Entity=[name=Violet Apprentice id=71 zone=PLAY zonePos=3 cardId=NEW1_026t player=2] tag=EXHAUSTED value=1
    TAG_CHANGE Entity=GameEntity tag=PROPOSED_ATTACKER value=0
    TAG_CHANGE Entity=GameEntity tag=PROPOSED_DEFENDER value=0
    TAG_CHANGE Entity=[name=Violet Apprentice id=71 zone=PLAY zonePos=3 cardId=NEW1_026t player=2] tag=ATTACKING value=0
    TAG_CHANGE Entity=[name=Rexxar id=4 zone=PLAY zonePos=0 cardId=HERO_05 player=1] tag=DEFENDING value=0
ACTION_END
"""

import re
import logging

class Entity(object):
    def __init__(self, **kwargs):
        """
        entity_id
        card_id
        """
        self.logger = logging.getLogger()
        self.tags = {}
        self.entity_id = None
        self.card_id = None

        for k, v in kwargs.items():
            setattr(self, k, v)

        if not self.entity_id:
            raise Exception("failed to set entity id! wtf?!")

    def update_tag(self, tag_name, tag_value):
        if tag_name in self.tags:
            old_str = " (old={})".format(self.tags[tag_name])
        else:
            old_str = ""
        self.logger.debug("Updating entity %s: tag %s=%s %s", self.entity_id, tag_name, tag_value, old_str)
        self.tags[tag_name] = self._cast_tag(tag_value)

    def get_tag(self, tag_name):
        return self.tags[tag_name]

    def _cast_tag(self, tag_value):
        try:
            int_value = int(tag_value)
            return int_value
        except:
            pass

        return tag_value

    def __repr__(self):
        try:
            card_str = self.name
        except AttributeError:
            card_str = self.id

        return card_str

def parse_tag_change(l):
    pattern = "\w*TAG_CHANGE Entity=\[(?P<ent_data>.+?)\] tag=(?P<tag_name>\S+) value=(?P<tag_value>\S+)"
    parse_results = re.match(pattern, l).groupdict()
    return {
        "ent_id": params_to_dict(parse_results["ent_data"])["id"],
        "tag_name": parse_results["tag_name"],
        "tag_value": parse_results["tag_value"]}

def parse_temp():
    l = "[Power] GameState.DebugPrintPower() - ACTION_START Entity=[name=Violet Ballin Apprentice id=71 zone=PLAY zonePos=3 cardId=NEW1_026t player=2] SubType=ATTACK Index=-1 Target=[name=Rexxar id=4 zone=PLAY zonePos=0 cardId=HERO_05 player=1]"
    pattern = "\[(?P<logger_name>\S+)\] (?P<log_source>\S+) - (?P<action_type>\S+) Entity=\[(?P<entity_data>.+?)\]"

    parse_results = re.match(pattern, l).groupdict()
    data = params_to_dict(parse_results["entity_data"])
    e = Entity(data["id"], data["name"])

    change_tag_line = "TAG_CHANGE Entity=[name=Violet Apprentice id=71 zone=PLAY zonePos=3 cardId=NEW1_026t player=2] tag=ATTACKING value=1"


