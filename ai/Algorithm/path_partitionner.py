from enum import Enum

import numpy as np
import numpy.matlib

from Util import Position
from Util.geometry import perpendicular, normalize
from Util.path import Path


class CollisionType(Enum):
    PLAYER = 0
    BALL = 1
    ZONE = 2


class CollisionBody:
    UNCOLLIDABLE = 0
    COLLIDABLE = 1

    def __init__(self, position: Position, velocity: Position=Position(), avoid_radius=1,
                 collision_type: CollisionType = CollisionType.PLAYER):
        self.position = position
        self.velocity = velocity
        self.avoid_radius = avoid_radius
        self.type = collision_type


class PathPartitionner:

    def __init__(self):
        self.path = Path()
        self.res = 100
        self.max_recurs = 3

        self.obstacles_position = None
        self.avoid_radius = np.array([])
        self.obstacles = None

        self.player = None
        self.target = None

    def fast_path_planner(self, path, depth=0, avoid_dir=None):
        self.fast_update_pertinent_collision_objects()
        if depth < self.max_recurs and not path.start == path.goal:
            if self.is_path_colliding(path):
                sub_target, avoid_dir = self.next_sub_target(path, avoid_dir)
                if sub_target != path.goal and sub_target != path.start:
                    path_1 = self.fast_path_planner(Path(path.start, sub_target), depth + 1, avoid_dir)
                    path_2 = self.fast_path_planner(Path(sub_target, path.goal), depth + 1, avoid_dir)
                    path = path_1.join_segments(path_2)

        return path

    def get_path(self, player: CollisionBody, target: CollisionBody, obstacles=None):

        self.target = target
        self.obstacles = obstacles
        self.player = player
        self.update_pertinent_collision_objects()
        self.path = Path(self.player.position, self.target.position)

        if any(self.obstacles):
            self.path = self.fast_path_planner(self.path)

        return self.path

    def update_pertinent_collision_objects(self):
        factor = 1.1
        consider_collision_body = []
        for collidable_object in self.obstacles:
            dist_player_to_obstacle = (self.player.position - collidable_object.position).norm
            dist_target_to_obstacle = (self.target.position - collidable_object.position).norm
            dist_target_to_player = (self.target.position - self.player.position).norm
            if dist_player_to_obstacle + dist_target_to_obstacle < dist_target_to_player * factor:
                consider_collision_body.append(collidable_object)
        self.obstacles_position = np.array([obstacle.position for obstacle in consider_collision_body])
        self.avoid_radius = np.array([obstacle.avoid_radius for obstacle in consider_collision_body])
        self.obstacles = consider_collision_body

    def fast_update_pertinent_collision_objects(self):
        temp = (self.path.start - self.obstacles_position) + (self.path.goal - self.obstacles_position)
        norm = np.sqrt((temp * temp).sum(axis=1))
        condition = norm < (self.path.goal - self.path.start).norm
        self.obstacles_position = self.obstacles_position[condition, :]
        self.obstacles = np.array(self.obstacles)[condition]
        self.avoid_radius = self.avoid_radius[condition]

    def is_path_colliding(self, path: Path, tolerance=1):

        if path.length < 50 or self.obstacles is None:
            return False

        closest_obstacle_pos = self.find_closest_obstacle(path, tolerance=tolerance)
        return closest_obstacle_pos is not None

    def find_closest_obstacle(self, path: Path, tolerance=1):

        if not any(self.obstacles):
            return None

        if path is None or path.length < 0.001:
            return None

        obstacles, distances = self.find_obstacles(path, tolerance=tolerance)

        if not np.any(obstacles):
            return None

        idx = np.argmin(distances)
        return obstacles[idx]

    def find_obstacles(self, path, tolerance=1):

        obstacles = self.obstacles_position

        if path.length < 0.0001 or obstacles is None:
            return None, 0

        points_start = np.array(path.points[:-1])
        points_target = np.array(path.points[1:])

        directions = points_target - points_start
        norm_directions = np.sqrt(np.square(directions).sum(axis=1))
        directions = directions / norm_directions
        directions = np.matlib.repmat(directions, obstacles.shape[0], 1)

        big_enough_paths = norm_directions > 0.000001
        points_start = points_start[big_enough_paths]

        position_obstacles = np.matlib.repmat(obstacles, 1, points_start.shape[0])
        position_robots = np.matlib.repmat(points_start, obstacles.shape[0], 1)
        vecs_robot_2_obs = position_obstacles - position_robots

        dist_robot_2_obs = np.sqrt(np.square(vecs_robot_2_obs).sum(axis=1))

        big_enough_dists = dist_robot_2_obs > 0.0000001
        dist_robot_2_obs = dist_robot_2_obs[big_enough_dists]
        dist_robot_2_obs = dist_robot_2_obs.reshape(dist_robot_2_obs.shape[0], 1)
        vec_robot_2_obs = vecs_robot_2_obs[big_enough_dists]

        directions_valid = directions[big_enough_dists]

        dists_from_path = np.abs(np.cross(directions_valid, vec_robot_2_obs))
        projection_obs_on_direction = (directions_valid * vec_robot_2_obs / dist_robot_2_obs).sum(axis=1)

        points_to_consider = np.abs(projection_obs_on_direction) < 1
        dists_to_consider = dists_from_path[points_to_consider]
        dists_to_consider = dists_to_consider.reshape(dists_to_consider.shape[0], 1)

        tolerances = self.avoid_radius / tolerance
        tolerances = np.matlib.repmat(tolerances, 1, points_start.shape[0]).T
        tolerances = tolerances[big_enough_dists]

        dists_to_consider_condition = np.abs(dists_to_consider) < tolerances
        dist_robot_2_obs = dist_robot_2_obs[dists_to_consider_condition]

        obstacles = np.array(self.obstacles)
        obstacles = np.array([obstacles[points_to_consider]]).T
        obstacles = obstacles[dists_to_consider_condition]

        return obstacles, dist_robot_2_obs

    def next_sub_target(self, path, avoid_dir=None):

        closest_obstacle = self.find_closest_obstacle(path)

        if closest_obstacle is None:
            return path.goal, avoid_dir

        start_to_goal = path.goal - path.start
        start_to_goal_direction = normalize(start_to_goal)
        start_to_closest_obstacle = closest_obstacle.position - path.start
        len_along_path = np.dot(start_to_closest_obstacle, start_to_goal_direction)

        resolution = closest_obstacle.avoid_radius / 10.

        if not (0 < len_along_path < start_to_goal.norm):
            sub_target = path.goal
        else:
            avoid_dir = perpendicular(start_to_goal_direction)
            sub_target = path.start + start_to_goal_direction * len_along_path - avoid_dir * self.res
            sub_target = self.optimize_sub_target(sub_target, -avoid_dir, res=resolution)

        return [sub_target, avoid_dir]

    def verify_sub_target(self, sub_target):
        dist_sub_2_obs = np.sqrt(((self.obstacles_position - sub_target) * (self.obstacles_position - sub_target)).sum(axis=1))
        if dist_sub_2_obs[dist_sub_2_obs < self.avoid_radius].any():
            return True
        return False

    def optimize_sub_target(self, initial_sub_target, avoid_dir, res):
        bool_sub_target_1 = self.verify_sub_target(initial_sub_target)
        sub_target = initial_sub_target
        while bool_sub_target_1:
            sub_target -= avoid_dir * res
            bool_sub_target_1 = self.verify_sub_target(sub_target)
            sub_target -= avoid_dir * 0.01 * res
        return sub_target.view(Position)
