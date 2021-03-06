# Under MIT license, see LICENSE.txt
import csv
import time
from typing import List

from Util import Pose
from ai.GameDomainObjects import Player
from Util.ai_command import Idle
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


class RobotIdent(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose, args: List[str]):
        super().__init__(game_state, player, target, args)
        self.status_flag = Flags.INIT
        self.cmd_filename = str(args[0])
        self.output_filename = str(args[1])
        self.cmd_id = 0
        self.start_time = 0
        self.commands = []
        with open(self.cmd_filename, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                cmd = tuple(float(i) for i in row)
                self.commands.append(cmd)

        with open(self.output_filename, 'w') as f:
            f.write('time,px,vx,py,vy,pt,vt\n')

    def exec(self):
        if self.status_flag is not Flags.FAILURE and self.cmd_id < len(self.commands) - 1:
            self.status_flag = Flags.WIP

            # Creating speed pose
            #  speed_pose = Pose(self.commands[self.cmd_id])
            self.cmd_id += 1

            # Saving data
            px = self.player.pose.position.x / 1000.0
            vx = self.player.velocity[0]
            py = self.player.pose.position.y / 1000.0
            vy = self.player.velocity[1]
            pt = self.player.pose.orientation
            vt = self.player.velocity[2]

            if self.cmd_id == 0:
                self.start_time = time.time()
            t = time.time() - self.start_time

            with open(self.output_filename, 'a') as f:
                f.write('{},{},{},{},{},{},{}\n'.format(t, px, vx, py, vy, pt, vt))

            raise RuntimeError("You need to implement a open control loop in the rest of system")
            # next_action = AICommand(self.player, AICommandType.MOVE, **{"pose_goal": speed_pose,
            #                                                             "control_loop_type": AIControlLoopType.OPEN})
        else:
            next_action = Idle

        return next_action

    def halt(self):
        return super(RobotIdent, self).halt()
