# Under MIT License, see LICENSE.txt

from typing import Dict

from Util import Position


class Ball:
    def __init__(self, position=Position()):
        self._position = position
        self._velocity = Position()

    def update(self, new_dict: Dict):
        self.position = new_dict['position']
        self.velocity = new_dict['velocity']

    @property
    def position(self) -> Position:
        return self._position

    @position.setter
    def position(self, value):
        assert isinstance(value, Position)
        self._position = value

    @property
    def velocity(self) -> Position:
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        assert isinstance(value, Position)
        self._velocity = value
