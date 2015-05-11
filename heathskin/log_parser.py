import re
import logging

from entity import Entity
from utils import params_to_dict
from exceptions import ParseException, PreventableException


class LogParser(object):
    def __init__(self, game_state):
        self.game_state = game_state
        self.logger = logging.getLogger()

        self.parser_fns = {
            "GameState.DebugPrintPower()": self.parse_debug_print_power,
            "ZoneChangeList.ProcessChanges()":
                self.parse_zone_change_list_process_changes,
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
            "FatalErrorScene.Awake()": None,
            "PowerSpellController2.InitPowerSpell()": None,

            "Card.ActivateActorSpells_PlayToHand()": None,
            "Card.OnSpellFinished_PlayToHand_SummonIn()": None,
            "ZoneHand.CanAnimateCard()": None,
            "Card.OnSpellStateFinished_PlayToHand_OldActor_SummonOut()": None,
            "PowerProcessor.PrepareHistoryForCurrentTaskList()": None,
            "PowerSpellController1.InitPowerSpell()": None,
            "PowerSpellController1.InitPowerSounds()": None,
            "Entity.AddAttachment()": None,
            "RewardUtils.GetViewableRewards()": None,

            "BnetFriendMgr.OnBnetError()": None,
            "BnetWhisperMgr.OnBnetError()": None,

            "BobLog": self.match_bob_line

        }

        self.in_create_game = False
        self.in_full_entity = False
        self.in_action = False
        self.ent_in_progress = None

        self.game_started = False

    def feed_line(self, logger_name, log_source, log_msg):
        if log_source not in self.parser_fns:
            raise PreventableException(
                "got unknown log_source {}".format(log_source))

        parser = self.parser_fns[log_source]
        if parser is not None:
            parser(log_msg)

    def match_bob_line(self, line):
        screen_to_game_type = {
            "RegisterScreenTourneys": "play",
            "RegisterScreenForge": "arena",
            "RegisterScreenPractice": "practice",
            "RegisterScreenFriendly": "friendly",
            "RegisterFeatures": None,
            "RegisterScreenOptimizedLogin": None,
            "RegisterScreenEndOfGame": None,
            "RegisterScreenBox": None,
            "RegisterFriendChallenge": None,
            "RegisterProfileNotices": None,
            "RegisterCollectionManager": None,

            "RegisterFeatures": None,
            "RegisterScreenOptimizedLogin": None,
            "RegisterScreenLogin": None,
            "RegisterScreenCollectionManager": None
            }

        if line not in screen_to_game_type:
            raise PreventableException(
                "got unknown bob source {}".format(line))

        game_type = screen_to_game_type[line]
        if game_type is None:
            return

        self.game_state.set_game_type(game_type)

    def match_tag_line(self, line):
        pattern = "\s*tag=(?P<tag_name>\S+) value=(?P<tag_value>\S+)"
        results = re.match(pattern, line)
        if not results:
            raise ParseException(
                "Failed to match_tag_line on msg '{}'".format(line))
        else:
            return results.groupdict()

    def match_tag_action(self, line):
        '''
        two different ways for TAG_CHANGE events to come in:
        # TAG_CHANGE Entity=[id=21 cardId= type=INVALID zone=DECK zonePos=0 player=1] tag=ZONE_POSITION value=1
        # TAG_CHANGE Entity=austin tag=MULLIGAN_STATE value=DEALING
        '''  # noqa
        pattern = "\s*TAG_CHANGE Entity=(\[(?P<entity_data>.*)\]|(?P<entity_name>.*)) tag=(?P<tag_name>\S+) value=(?P<tag_value>\S+)"  # noqa
        results = re.match(pattern, line)
        if not results:
            raise ParseException(
                "failed to parse TAG_CHANGE action for msg '{}'".format(line))

        results = results.groupdict()
        if results['entity_data'] is not None:
            entity_id = params_to_dict(results['entity_data'])['id']
            results['entity_name'] = entity_id

        results.pop('entity_data')

        return results

    def match_show_entity_action(self, line):
        '''
        SHOW_ENTITY - Updating Entity=[id=21 cardId= type=INVALID zone=DECK zonePos=0 player=1] CardID=EX1_539
        SHOW_ENTITY - Updating Entity=69 CardID=CS2_005o
        '''  # noqa
        pattern = "SHOW_ENTITY - Updating Entity=((?P<entity_id>\d+)|\[(?P<entity_data>.*)\]) CardID=(?P<card_id>.+)"  # noqa

        results = re.match(pattern, line)
        if not results:
            raise ParseException(
                "failed to parse SHOW_ENTITY action for msg '{}'".format(line))

        results = results.groupdict()
        if results['entity_data'] is not None:
            results['entity_data'] = params_to_dict(results['entity_data'])
        else:
            results['entity_data'] = {'id': results['entity_id']}

        return results

    def match_hide_entity_action(self, line):
        # HIDE_ENTITY - Entity=[name=Mechwarper id=54 zone=HAND zonePos=2 cardId=GVG_006 player=2] tag=ZONE value=DECK
        pattern = "HIDE_ENTITY - Entity=\[(?P<entity_data>.*)\] tag=(?P<tag_name>\S+) value=(?P<tag_value>\S+)"  # noqa
        results = re.match(pattern, line)
        if not results:
            raise ParseException(
                "failed to parse HIDE_ENTITY action for msg '{}'".format(line))
        results = results.groupdict()
        results['entity_data'] = params_to_dict(results['entity_data'])

        return results

    def parse_debug_print_power(self, msg):
        # leave/continue CREATE_GAME
        if self.in_create_game:
            # leave CREATE_GAME
            if not msg.startswith(" "):
                self.logger.info("Finished initial game creation")
                self.in_create_game = False
                self.game_started = True

            # set tag on entity created during CREATE_GAME
            elif msg.lstrip().startswith("tag"):
                results = self.match_tag_line(msg)
                self.ent_in_progress.update_tag(**results)
                return

            # create new entity during CREATE_GAME
            else:
                msg = msg.lstrip()
                # GameEntity EntityID=1
                # Player EntityID=2 PlayerID=1 GameAccountId=[hi=144115193835963207 lo=34493978]
                # XXX: this does not parse out the game account id. maybe useless anyway?
                pattern = "(?P<entity_type>GameEntity|Player) EntityID=(?P<entity_id>\d+)"  # noqa
                results = re.match(pattern, msg)
                if not results:
                    raise Exception("nice try asshole '{}'".format(msg))
                results = results.groupdict()

                self.logger.debug(
                    "Creating entity of type %s with id %s during initial create game",
                    results['entity_type'],
                    results['entity_id'])

                ent = Entity(**results)
                if ent.entity_id in self.game_state.entities:
                    raise Exception("fuckup")

                self.game_state.entities[ent.entity_id] = ent
                self.ent_in_progress = ent
                return

        # enter CREATE_GAME
        if msg == "CREATE_GAME":
            self.logger.info("Found initial game creation")
            self.in_create_game = True
            return

        # dont proceed with parsing unless the game has started
        if not self.game_started:
            self.logger.info("game not started, skipping line '%s'", msg)
            return

        # leave/continue FULL_ENTITY
        if self.in_full_entity:
            if not msg.startswith(" "):
                self.logger.debug(
                    "Finished entity creation for id %s",
                    self.ent_in_progress.entity_id)
                self.in_full_entity = False
                self.ent_in_progress = None
            else:
                # tag=HEALTH value=1
                try:
                    results = self.match_tag_line(msg)
                    self.ent_in_progress.update_tag(**results)
                    return
                except ParseException:
                    # XXX: this is an ugly hack to get around the fact that
                    # FULL_ENTITY actions inside ACTION_START blocks end
                    # without any delimiters. all that changes is the indent
                    # level. this pass lets us drop into the in_action handler
                    # below, which will correctly pick up whatever the next
                    # sub-action is
                    self.in_full_entity = False
                    self.ent_in_progress = None
                    self.logger.debug("hit the expected parse exception")
                    pass

        # enter FULL_ENTITY
        if msg.startswith("FULL_ENTITY"):
            self.parse_full_entity(msg)
            return

        # handle in_action
        if self.in_action:
            if msg == "ACTION_END":
                self.logger.debug("Closed ACTION")
                self.in_action = False
                self.ent_in_progress = False
            elif msg.startswith(' '):
                msg = msg.lstrip()
                if msg.startswith("TAG_CHANGE"):
                    self.logger.debug("starting sub-action TAG_CHANGE")
                    self._tag_change(msg)
                elif msg.startswith("SHOW_ENTITY"):
                    self.logger.debug("starting sub-action SHOW_ENTITY")
                    results = self.match_show_entity_action(msg)
                    entity_id = results['entity_data']['id']
                    target_ent = self.game_state.entities[entity_id]
                    target_ent.card_id = results['card_id']

                # this happens after unstable portal, for example
                elif msg.startswith("FULL_ENTITY"):
                    self.logger.debug("starting sub-action FULL_ENTITY")
                    self.parse_full_entity(msg)

                elif msg.startswith("tag"):
                    self.match_tag_line(msg)

                elif msg.startswith("HIDE_ENTITY"):
                    self.logger.info("starting sub-action HIDE_ENTITY")
                    results = self.match_hide_entity_action(msg)
                    entity_id = results['entity_data']['id']

                    target_ent = self.game_state.entities[entity_id]
                    target_ent.update_tag(
                        results['tag_name'], results['tag_value'])

                elif msg.startswith("ACTION_START") or msg.startswith("ACTION_END"):
                    # XXX: afaict, these are noops...
                    pass

                elif msg.startswith("META_DATA"):
                    # XXX: this is not a noop, but i dont know what to do...
                    pass

                else:
                    raise Exception("unknown PRINT_POWER: '{}'".format(msg))

            return

        # enter ACTION_START
        if msg.startswith("ACTION_START"):
            self.logger.debug("Opened ACTION")
            self.in_action = True
            return

        # tag change
        if msg.startswith("TAG_CHANGE"):
            self._tag_change(msg)
            return

        self.logger.info("debug power msg: %s", msg)


    def _tag_change(self, msg):
        """ applies a tag change to an entity
        """
        self.logger.debug("tag change msg: %s", msg)
        results = self.match_tag_action(msg)
        self._setup_players_from_entity_name(results)
        entity_name = results.pop('entity_name')
        if results.get('tag_name') == 'ENTITY_ID' and entity_name != "GameEntity":
            self.game_state.players[entity_name].update({
                'entity_id': results.get('tag_value')
            })
        player = self.game_state.players.get(entity_name)
        target_ent = None
        if player and player.get('entity_id'):
            target_ent = self.game_state.entities.get(player.get('entity_id'))
        elif not player:
            target_ent = self.game_state.get_entity_by_name(entity_name)

        if not target_ent:
            return
            # XXX
            # raise PreventableException("failed to handle tag change for msg: '{}'".format(msg))

        target_ent.update_tag(**results)
        # if results.get('tag_name') == 'DAMAGE':
        #     self.logger.debug(
        #         "DAMAGE tag change entity: %s, player 1 health: %s, player 2 health: %s",
        #         target_ent,
        #         self.game_state._get_player_healths()[0],
        #         self.game_state._get_player_healths()[1]
        #         )

    def _setup_players_from_entity_name(self, results):
        """
        The player's username that appears first is player1 (first to act)
        check to see if we have seen a username yet.. if not set it to this
        first username and otherwise check to see if it is a new username
        and if so set it to player2
        """
        entity_name = results.get('entity_name')
        if len(self.game_state.players) == 0:
            self.game_state.players[entity_name] = {
                'username': entity_name,
                'first': True,
            }
        elif len(self.game_state.players) == 1:
            if entity_name not in self.game_state.players.keys():
                self.game_state.players[entity_name] = {
                    'username': entity_name,
                }

    def parse_zone_change_list_process_changes(self, msg):
        if not self.game_started:
            return

        useless_starts = [
            "START waiting",
            "END waiting",
            "processing",
            "m_id=",
            "id="]

        for s in useless_starts:
            if msg.startswith(s):
                return
        if msg.startswith("TRANSITIONING"):
            # TRANSITIONING card [name=Kill Command id=21 zone=HAND zonePos=0 cardId=EX1_539 player=1] to FRIENDLY HAND
            pattern = "TRANSITIONING card \[(?P<entity_data>.+?)\] to( (?P<dest_zone>.+)|)"  # noqa
            result = re.match(pattern, msg)
            if not result:
                raise Exception("failed parse on msg '{}'".format(msg))

            result = result.groupdict()

            ent_data = params_to_dict(result['entity_data'])
            target_ent = self.game_state.entities[ent_data['id']]
            target_ent.update_tag("ZONE", result['dest_zone'])

            # Spells being cast transition to nothing, manually set here
            if result['dest_zone'] is None:
                target_ent.update_tag("ZONE", 'CASTING SPELL')
                return

    def parse_ignore(self, msg):
        self.logger.debug("parser ignoring msg: '%s'", msg)

    def parse_full_entity(self, msg):
        self.logger.debug("Starting full entity %s", msg)
        self.in_full_entity = True
        pattern = "FULL_ENTITY - Creating ID=(?P<entity_id>\d+) CardID=(?P<card_id>\S*)"  # noqa
        results = re.match(pattern, msg)

        if not results:
            raise Exception("parse failure on msg '{}'".format(msg))
        else:
            ent = Entity(**results.groupdict())
            if ent.entity_id in self.game_state.entities:
                raise Exception("hurr durr i got it wrong")

            self.logger.debug("Creating entity with ID %s", ent.entity_id)
            self.game_state.entities[ent.entity_id] = ent
            self.ent_in_progress = ent
