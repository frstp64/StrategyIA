# Under MIT License, see LICENSE.txt

from functools import partial
from random import shuffle

from RULEngine.Util.Pose import Position, Pose
from ai.STA.Strategy.Strategy import Strategy
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.STA.Tactic.DemoFollowBall import DemoFollowBall
from ai.STA.Tactic.DemoFollowRobot import DemoFollowRobot
from ai.STA.Tactic.goToPositionPathfinder import GoToPositionPathfinder
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.Joystick import Joystick
from ai.Util.role import Role


class BambaFollow(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        p1 = self.game_state.get_player_by_role(Role.FIRST_ATTACK)
        p2 = self.game_state.get_player_by_role(Role.SECOND_ATTACK)
        p3 = self.game_state.get_player_by_role(Role.MIDDLE)

        self.add_tactic(Role.FIRST_ATTACK, DemoFollowBall(self.game_state, p1))
        self.add_tactic(Role.SECOND_ATTACK, DemoFollowRobot(self.game_state, p2, args=[p1.id]))
        self.add_tactic(Role.MIDDLE, DemoFollowRobot(self.game_state, p3, args=[p2.id]))



