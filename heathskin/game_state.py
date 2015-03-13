import re
import logging
from collections import defaultdict

from utils import params_to_dict
from entity import Entity

class GameState(object):
    def __init__(self, friendly_user_name=None, friendly_deck=None):
        self.entities = {}
        self.friendly_user_name = friendly_user_name
        self.friendly_deck = friendly_deck
        self.logger = logging.getLogger()

        self.parser_fns = {
            "GameState.DebugPrintPower()": self.parse_debug_print_power,
            "ZoneChangeList.ProcessChanges()": self.parse_zone_change_list_process_changes,
            "ZoneChangeList.UpdateDirtyZones()": None,
            "PowerProcessor.BeginCurrentTaskList()": self.parse_ignore,
            "PowerProcessor.EndCurrentTaskList()": self.parse_ignore,
            "ZoneChangeList.OnUpdateLayoutComplete()": None,
            "ZoneChangeList.Finish()": None,
            "GameState.DebugPrintPowerList()": None,
            "PowerProcessor.DoTaskListForCard()": None,
            "ZoneChangeList.FireCompleteCallback()": None,
            "ZoneMgr.AddServerZoneChanges()": None,
            "SeedMaterialEffects()": None,
            "GameState.DebugPrintOptions()": None,
            "GameState.DebugPrintChoice()": None,
            "Card.SetDoNotSort()": None,
            "GameState.SendOption()": None,
            "ZoneMgr.CreateLocalChangesFromTrigger()": None,
            "Card.MarkAsGrabbedByEnemyActionHandler()": None,
            "NetCache.OnProfileNotices()": None,
            "GameState.SendChoices()": None,
            "ZoneMgr.CreateLocalChangeList()": None,
            "ZoneMgr.ProcessLocalChangeList()": None,
        }

        self.in_create_game = False
        self.in_full_entity = False
        self.ent_in_progress = None

    def feed_line(self, line):
        pattern = "\[(?P<logger_name>\S+)\] (?P<log_source>\S+\(\)) - (?P<log_msg>.*)"
        results = re.match(pattern, line)
        if not results:
            return

        results = results.groupdict()
        if results['log_source'] not in self.parser_fns:
            raise Exception("lolwut, got unknown log source '{}'".format(results['log_source']))

        parser = self.parser_fns[results['log_source']]
        if parser:
            parser(results['log_msg'])

        self.logger.debug("total of %d entities", len(self.entities))

    def parse_debug_print_power(self, msg):
        # leave/continue CREATE_GAME
        if self.in_create_game:
            # leave CREATE_GAME
            if not msg.startswith(" "):
                self.logger.info("Finished initial game creation")
                self.in_create_game = False

            # set tag on entity created during CREATE_GAME
            elif msg.lstrip().startswith("tag"):
                pattern = "\s+tag=(?P<tag_name>\S+) value=(?P<tag_value>\S+)"
                results = re.match(pattern, msg)
                if not results:
                    raise Exception("lolwut '{}'".format(msg))
                else:
                    #self.logger.info("got a match from %s %s", msg, results.groupdict())
                    self.ent_in_progress.update_tag(**results.groupdict())
                    return

            # create new entity during CREATE_GAME
            else:
                msg = msg.lstrip()
                # GameEntity EntityID=1
                # Player EntityID=2 PlayerID=1 GameAccountId=[hi=144115193835963207 lo=34493978]
                # XXX: this does not parse out the game account id. maybe useless anyway?
                pattern = "(?P<entity_type>GameEntity|Player) EntityID=(?P<entity_id>\d+)"
                results = re.match(pattern, msg)
                if not results:
                    raise Exception("nice try asshole '{}'".format(msg))
                results = results.groupdict()

                self.logger.info(
                    "Creating entity of type %s with id %s during initial create game",
                    results['entity_type'],
                    results['entity_id'])

                ent = Entity(**results)
                if ent.entity_id in self.entities:
                    raise Exception("fuckup")

                self.entities[ent.entity_id] = ent
                self.ent_in_progress = ent
                return

        # enter CREATE_GAME
        if msg == "CREATE_GAME":
            self.logger.info("Found initial game creation")
            self.in_create_game = True
            return

        # leave/continue FULL_ENTITY
        if self.in_full_entity:
            if not msg.startswith(" "):
                self.logger.debug("Finished entity creation for id %s", self.ent_in_progress.entity_id)
                self.in_full_entity = False
            else:
                # tag=HEALTH value=1
                pattern = "\s+tag=(?P<tag_name>\S+) value=(?P<tag_value>\S+)"
                results = re.match(pattern, msg)
                if not results:
                    raise Exception("lolwut '{}'".format(msg))
                else:
                    #self.logger.info("got a match %s", results.groupdict())
                    self.ent_in_progress.update_tag(**results.groupdict())
                    return

        # enter FULL_ENTITY
        if msg.startswith("FULL_ENTITY"):
            self.logger.debug("Starting full entity %s", msg)
            self.in_full_entity = True
            pattern = "FULL_ENTITY - Creating ID=(?P<entity_id>\d+) CardID=(?P<card_id>\S*)"
            results = re.match(pattern, msg)

            if not results:
                sys.exit()
            else:
                ent = Entity(**results.groupdict())
                if ent.entity_id in self.entities:
                    raise Exception("hurr durr i got it wrong")

                self.logger.debug("Creating entity with ID %s", ent.entity_id)
                self.entities[ent.entity_id] = ent
                self.ent_in_progress = ent
                return

        # tag change
        if msg.startswith("TAG_CHANGE"):
            # TAG_CHANGE Entity=Ryan Higdon tag=TIMEOUT value=75
            pattern = "TAG_CHANGE Entity=(?P<entity_name>.*) tag=(?P<tag_name>\S+) value=(?P<tag_value>\S+)"
            results = re.match(pattern, msg)
            if not results:
                sys.exit()
            else:
                results = results.groupdict()
                self.logger.info(msg)
                self.logger.info("tag change msg %s", results)
                entity_name = results.pop('entity_name')
                target_ent = self.get_entity_by_name(entity_name)

                target_ent.update_tag(**results)
                return


        self.logger.info("debug power msg: %s", msg)
            #print "debug power:", msg

    def parse_zone_change_list_process_changes(self, msg):
        useless_starts = ["START waiting", "END waiting", "processing", "m_id=", "id="]
        for s in useless_starts:
            if msg.startswith(s):
                return
        if msg.startswith("TRANSITIONING"):
            pattern = "TRANSITIONING card \[(?P<entity_data>.+?)\] to( (?P<dest_zone>.+)|)"
            result = re.match(pattern, msg)
            if not result:
                self.logger.error("total fuck %s", msg)
            else:
                #print "got this", result.groupdict()
                if result.groupdict()['dest_zone'] == None:
                    self.logger.error("no zone, msg was %s", msg)

            #print "zonechange:", msg

    def parse_ignore(self, msg):
        self.logger.debug("parser ignoring msg: '%s'", msg)

    def convert_log_zone(self, log_zone):
        if not log_zone:
            return log_zone
        log_zone = "".join([c for c in log_zone.lower() if c not in ["(", ")"]])

        result = "_".join(log_zone.split(" "))
        return result

    def get_entity_by_name(self, ent_id):
        result_id = None
        try:
            int(ent_id)
            result_id = ent_id
        except ValueError:
            if ent_id == "GameEntity":
                result_id = "1"
            elif ent_id == self.friendly_user_name:
                result_id = "2"
            else:
                result_id = "3"

        self.logger.info("Converted entity name '%s' to id %s", ent_id, result_id)
        return self.entities[result_id]



