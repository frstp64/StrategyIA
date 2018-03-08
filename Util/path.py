import numpy as np

from Util import Position


class Path:
    # FIXME remove speed from pathfinder, it shouldn't be its concern
    # TODO: Instead of start and end, should it be more logical to have the list of points?
    def __init__(self, start=Position(),  end=Position(), start_speed=0, end_speed=0):

        self.points = [start, end]
        self.speeds = [start_speed, end_speed]
        self.turns = self.points

    def join_segments(self, other):
        new_path = Path()
        new_path.points = self.points+other.points[1:]
        return new_path

    def split_path(self, idx):
        if idx < 1:
            path_1 = Path()
            path_2 = self
        else:
            path_1 = Path()
            path_1.points = self.points[:idx+1]
            path_2 = Path()
            path_2.points = self.points[idx:]
        return path_1, path_2

    @staticmethod
    def generate_path_from_points(points_list, speed_list=None, threshold=None, turns_list=None):
        if speed_list is None or len(speed_list) < 2:
            speed_list = [0, 0]
        if len(points_list) < 2:
            points_list = [points_list[0], points_list[0]] # Why?
        if len(points_list) < 3:
            pass
        elif threshold is not None:
            for i in range(0, len(points_list)-1):
                if np.linalg.norm(points_list[i] - points_list[i+1]) < threshold:
                    del points_list[i+1]
        # points étant une liste de positions
        new_path = Path()
        if turns_list is None or len(turns_list) < 2:
            turns_list = [new_path.start, new_path.goal]
        new_path.points = points_list
        new_path.speeds = speed_list
        new_path.turns = turns_list

        return new_path

    @property
    def start(self):
        return self.points[0]

    @start.setter
    def start(self, v):
        self.points[0] = v

    @property
    def goal(self):
        return self.points[-1]

    @goal.setter
    def goal(self, v):
        self.points[-1] = v

    @property
    def length(self):
        segments = [(point - next_point).view(Position).norm for point, next_point in zip(self.points, self.points[1:])]
        return sum(segments)

    def quick_update_path(self, position):
        self.points[0] = position
        new_path = Path().generate_path_from_points(self.points, self.speeds, None)
        self.points = new_path.points
        self.speeds = new_path.speeds
        self.turns = new_path.turns

    def copy(self):
        new_path = Path()
        new_path.points = self.points.copy()
        new_path.speeds = self.speeds.copy()
        new_path.turns = self.turns.copy()
        return new_path

    def __iter__(self):
        for p in self.points:
            yield p

    def __len__(self):
        return len(self.points)
