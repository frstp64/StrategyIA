# Under MIT license, see LICENSE.txt

from Util import Pose, AICommand
from ai.GameDomainObjects import Player
from ai.STA.Action import Action
from ai.states.game_state import GameState


class MoveToPosition(Action):

    def __init__(self, game_state: GameState, player: Player, destination: Pose, cruise_speed=1, ball_collision=True):
        Action.__init__(self, game_state, player)
        assert isinstance(destination, Pose)

        self.destination = destination
        self.cruise_speed = cruise_speed
        self.ball_collision = ball_collision

    def exec(self):
        return AICommand(self.player.id, self.destination,
                         cruise_speed=self.cruise_speed,
                         ball_collision=self.ball_collision)
