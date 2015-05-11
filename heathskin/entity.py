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
"""  # noqa

import logging

from heathskin import card_database


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
        self.card_db = card_database.CardDatabase.get_database()

        self.tag_history = []

        for k, v in kwargs.items():
            setattr(self, k, v)

        if not self.entity_id:
            raise Exception("failed to set entity id! wtf?!")

    def update_tag(self, tag_name, tag_value):
        if tag_name in self.tags:
            old_str = self.tags[tag_name]
        else:
            old_str = "None"

        new_event = EntityChangeEvent(tag_name, old_str, tag_value)
        self.tag_history.append(new_event)

        self.logger.info(
            "Updating %s %s",
            self.__repr__(), new_event.__str__())
        self.tags[tag_name] = self._cast_tag(tag_value)

    def get_tag(self, tag_name, default=None):
        return self.tags.get(tag_name, default)

    def get_source_zone(self):
        for event in self.tag_history:
            if event.tag_name == "ZONE":
                return event.old_value
        self.logger.debug("No source zone: {}, event: {}".format(
            str(self), event.tag_name))
        return None

    def _cast_tag(self, tag_value):
        try:
            int_value = int(tag_value)
            return int_value
        except:
            pass

        return tag_value

    def __repr__(self):
        if self.card_id:
            name = self.card_db.get_card_by_id(self.card_id)['name']
            card_str = "name='{}'".format(name)
        else:
            card_str = "entity_id={}".format(self.entity_id)

        return "[Entity {}]".format(card_str)


    @property
    def name(self):
        if self.card_id:
            name = self.card_db.get_card_by_id(self.card_id)['name']
            return name
        return None

class EntityChangeEvent(object):
    def __init__(self, tag_name, old_value, new_value):
        self.tag_name = tag_name
        self.old_value = old_value
        self.new_value = new_value

    def __str__(self):
        return "{} [{} -> {}]".format(
            self.tag_name, self.old_value, self.new_value)
