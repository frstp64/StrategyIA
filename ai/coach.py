# Under MIT License, see LICENSE.txt
import logging
import os
import cProfile

from multiprocessing import Process, Queue
from multiprocessing.managers import DictProxy
from time import time
from typing import List

from Util.engine_command import EngineCommand
from Util.team_color_service import TeamColorService
from Util.timing import create_fps_timer
from ai.executors.debug_executor import DebugExecutor
from ai.executors.play_executor import PlayExecutor
from ai.states.game_state import GameState
from ai.states.play_state import PlayState
from config.config import Config


class Coach(Process):

    MAX_EXCESS_TIME = 0.1
    PROFILE_DATA_TIME = 10
    PROFILE_DATA_FILENAME = 'profile_data_ai.prof'

    def __init__(self,
                 engine_game_state: DictProxy,
                 field: DictProxy,
                 ai_queue: Queue,
                 referee_queue: Queue,
                 ui_send_queue: Queue,
                 ui_recv_queue: Queue):

        super().__init__(name=__name__)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.cfg = Config()

        self.mode_debug_active = self.cfg['DEBUG']['using_debug']
        self.is_simulation = self.cfg['GAME']['type'] == 'sim'

        # Managers for shared memory between process
        self.engine_game_state = engine_game_state
        self.field = field

        # Queues for interprocess communication with the engine
        self.ai_queue = ai_queue
        self.referee_queue = referee_queue
        self.ui_send_queue = ui_send_queue
        self.ui_recv_queue = ui_recv_queue

        # the states
        self.team_color_service = TeamColorService()
        self.game_state = GameState()
        self.play_state = PlayState()

        # the executors
        self.play_executor = PlayExecutor(self.play_state, self.ui_send_queue)
        self.debug_executor = DebugExecutor(self.play_state, self.play_executor, self.ui_send_queue, self.ui_recv_queue)

        # print frame rate
        self.fps = 1/self.cfg['GAME']['ai_timestamp']
        self.frame_count = 0
        self.time_last_print = time()
        self.last_frame_count = 0

        def callback(excess_time):
            if excess_time > Coach.MAX_EXCESS_TIME:
                self.logger.debug('Overloaded (%.1f ms behind schedule)', 1000*excess_time)

        self.fps_sleep = create_fps_timer(self.fps, on_miss_callback=callback)

        # profiling
        self.profiling_enabled = False
        self.profiler = None


    def wait_for_geometry(self):
        self.logger.debug('Waiting for geometry from the Engine.')
        start = time()
        while not self.field:
            self.fps_sleep()
        self.logger.debug('Geometry received from the Engine in {:0.2f} seconds.'.format(time() - start))

    def run(self) -> None:
        self.wait_for_geometry()
        self.logger.debug('Running with process ID {}'.format(os.getpid()))

        try:
            while True:
                self.frame_count += 1
                self.main_loop()
                self.dump_profiling_stats()
                self.fps_sleep()
        except KeyboardInterrupt:
            pass

    def main_loop(self) -> None:
        self.game_state.update(self.engine_game_state)
        self.debug_executor.exec()
        engine_commands = self.play_executor.exec()
        self._send_cmd(engine_commands)

    def _send_cmd(self, engine_commands: List[EngineCommand]):
        self.ai_queue.put(engine_commands)

    def enable_profiling(self):
        self.profiling_enabled = True
        self.profiler = cProfile.Profile()
        self.profiler.enable()
        self.logger.debug('Profiling mode activate.')

    def dump_profiling_stats(self):
        if self.profiling_enabled:
            if self.frame_count % (self.fps * Coach.PROFILE_DATA_TIME) == 0:
                self.profiler.dump_stats(Coach.PROFILE_DATA_FILENAME)
                self.logger.debug('Profile data written to {}.'.format(Coach.PROFILE_DATA_FILENAME))

