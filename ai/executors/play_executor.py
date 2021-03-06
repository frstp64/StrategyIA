# Under MIT License, see LICENSE.txt

import logging
from multiprocessing import Queue

from typing import List, Dict

from Debug.debug_command_factory import DebugCommandFactory
from Util import Pose, Position, AICommand, EngineCommand
from ai.Algorithm.auto_play import SimpleAutoPlay
from ai.GameDomainObjects import Player
from ai.STA.Strategy.human_control import HumanControl
from ai.Util.sta_change_command import STAChangeCommand
from ai.executors.pathfinder_module import PathfinderModule
from ai.states.game_state import GameState
from ai.states.play_state import PlayState
from config.config import Config


class PlayExecutor:

    def __init__(self, play_state: PlayState, ui_send_queue: Queue):
        self.logger = logging.getLogger(self.__class__.__name__)

        cfg = Config()
        self.auto_play = SimpleAutoPlay(play_state)
        self.play_state = play_state
        self.game_state = GameState()
        self.play_state.autonomous_flag = cfg["GAME"]["autonomous_play"] == "true"
        self.last_available_players = {}
        self.goalie_id = -1
        self.ui_send_queue = ui_send_queue

        self.pathfinder_module = PathfinderModule()

    def exec(self) -> List[EngineCommand]:
        """
        Execute la stratégie courante et envoie le status des robots et les livres de tactiques et stratégies

        :return: None
        """

        # if self.play_state.autonomous_flag:
        #     if GameState().game.referee.team_info['ours']['goalie'] != self.goalie_id:
        #         self.goalie_id = GameState().game.referee.team_info['ours']['goalie']
        #         GameState().update_player_for_locked_role(self.goalie_id, Role.GOALKEEPER)
        #     self.auto_play.update(self._has_available_players_changed())
        ai_cmds = self._execute_strategy()
        engine_cmds = []

        paths = self.pathfinder_module.exec(self.game_state, ai_cmds)

        for player, ai_cmd in ai_cmds.items():
            engine_cmds.append(generate_engine_cmd(player, ai_cmd, paths[player]))

        self._send_robots_status()

        return engine_cmds

    def order_change_of_sta(self, cmd: STAChangeCommand):
        if cmd.is_strategy_change_command():
            self._change_strategy(cmd)
        elif cmd.is_tactic_change_command():
            self._change_tactic(cmd)

    def _change_strategy(self, cmd: STAChangeCommand):
        self.play_state.current_strategy = cmd.data["strategy"]

    def _change_tactic(self, cmd: STAChangeCommand):

        try:
            this_player = GameState().our_team.available_players[cmd.data['id']]
        except KeyError:
            self.logger.debug("Invalid player id: {}".format(cmd.data['id']))
            return
        player_id = this_player.id
        tactic_name = cmd.data['tactic']
        target = cmd.data['target']
        target = Pose(Position(target[0], target[1]), this_player.pose.orientation)
        args = cmd.data.get('args', "")
        try:
            tactic = self.play_state.get_new_tactic(tactic_name)(GameState(), this_player, target, args)
        except Exception as e:
            self.logger.debug(e)
            self.logger.debug("La tactique n'a pas été appliquée par cause de mauvais arguments.")
            raise e

        if not isinstance(self.play_state.current_strategy, HumanControl):
            self.play_state.current_strategy = "HumanControl"
        self.play_state.current_strategy.assign_tactic(tactic, player_id)

    def _execute_strategy(self) -> Dict[Player, AICommand]:
        # Applique un stratégie par défault s'il n'en a pas (lors du démarage par exemple)
        # Apply the default strategy if there is none (for example at startup)
        if self.play_state.current_strategy is None:
            self.play_state.current_strategy = "DoNothing"
        return self.play_state.current_strategy.exec()

    def _send_robots_status(self) -> None:
        states = self.play_state.current_tactical_state
        cmds = []
        for player, tactic_name, action_name, target in states:
            if action_name != 'Stop':
                cmd = DebugCommandFactory.robot_strategic_state(player,
                                                                tactic_name,
                                                                action_name,
                                                                target.position.to_tuple())
                cmds.append(cmd)
        self.ui_send_queue.put(cmds)

    # def _has_available_players_changed(self) -> bool:
    #     available_players = GameState().our_team.available_players
    #     player_change = False
    #     for i in available_players:
    #         if i not in self.last_available_players:
    #             player_change = True
    #             break
    #     if not player_change:
    #         for i in self.last_available_players:
    #             if i not in available_players:
    #                 player_change = True
    #                 break
    #     self.last_available_players = available_players.copy()
    #     return player_change


def generate_engine_cmd(player: Player, ai_cmd: AICommand, path):
    return EngineCommand(player.id,
                         cruise_speed=ai_cmd.cruise_speed * 1000,
                         path=path,
                         kick_type=ai_cmd.kick_type,
                         kick_force=ai_cmd.kick_force,
                         dribbler_active=ai_cmd.dribbler_active,
                         target_orientation=ai_cmd.target.orientation if ai_cmd.target else None,
                         end_speed=ai_cmd.end_speed,
                         charge_kick=ai_cmd.charge_kick)
