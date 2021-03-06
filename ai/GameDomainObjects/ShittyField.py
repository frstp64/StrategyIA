# Under MIT License, see LICENSE.txt
from enum import Enum

from Util import Position
from ai.GameDomainObjects import Ball
# from Engine.Debug.debug_interface import DebugInterface
from config.config import Config


class FieldSide(Enum):
    POSITIVE = 0
    NEGATIVE = 1


# noinspection PyPep8
class FieldCircularArc:
    def __init__(self, protobuf_arc):
        self.center = Position(protobuf_arc.center.x,
                               protobuf_arc.center.y)
        self.radius      = protobuf_arc.radius
        self.angle_start = protobuf_arc.a1  # Counter clockwise order
        self.angle_ened  = protobuf_arc.a2
        self.thickness   = protobuf_arc.thickness


class FieldLineSegment:
    def __init__(self, protobuf_line):
        self.p1 = Position(protobuf_line.p1.x, protobuf_line.p1.y)
        self.p2 = Position(protobuf_line.p2.x, protobuf_line.p2.y)
        self.length = (self.p2 - self.p1).norm
        self.thickness = protobuf_line.thickness


# noinspection PyPep8,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyMethodMayBeStatic,PyMethodMayBeStatic,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences
class ShittyField:
    def __init__(self, ball: Ball):
        self.ball = ball
        # self.debug_interface = DebugInterface()
        cfg = Config()

        if cfg["GAME"]["our_side"] == "positive":
            self.our_side = FieldSide.POSITIVE
            self.constant = positive_side_constant
        else:
            self.our_side = FieldSide.NEGATIVE
            self.constant = negative_side_constant

    # noinspection PyUnusedLocal
    def set_collision_body(self):
        x_their_goal = self.constant["FIELD_THEIR_GOAL_X_EXTERNAL"]
        x_our_goal = self.constant["FIELD_OUR_GOAL_X_EXTERNAL"]
        radius = self.constant["FIELD_GOAL_RADIUS"]

        # self.field_collision_body = [CollisionBody(Position(x_their_goal, 0), Position(0, 0), radius, CollisionType.ZONE),
        #                              CollisionBody(Position(x_our_goal, 0), Position(0, 0), radius, CollisionType.ZONE)]

        # self.debug_interface.add_circle((x_their_goal, 0), radius=radius, timeout=0, color=(255, 0, 0))
        # self.debug_interface.add_circle((x_our_goal, 0), radius=radius, timeout=0, color=(255, 0, 0))

    def is_inside_goal_area(self, position, dist_from_goal_area=0, our_goal=True):
        assert (isinstance(position, Position))
        assert (isinstance(our_goal, bool))
        x1 = self.constant["FIELD_OUR_GOAL_X_EXTERNAL"] if our_goal else self.constant["FIELD_THEIR_GOAL_X_EXTERNAL"]
        x2 = self.constant["FIELD_OUR_GOAL_X_INTERNAL"] if our_goal else self.constant["FIELD_THEIR_GOAL_X_INTERNAL"]

        x_right = max(x1, x2) + dist_from_goal_area
        x_left = min(x1, x2) - dist_from_goal_area

        top_circle = self.constant["FIELD_OUR_GOAL_TOP_CIRCLE"] if our_goal\
            else self.constant["FIELD_THEIR_GOAL_TOP_CIRCLE"]
        bot_circle = self.constant["FIELD_OUR_GOAL_BOTTOM_CIRCLE"] if our_goal\
            else self.constant["FIELD_THEIR_GOAL_BOTTOM_CIRCLE"]
        if isInsideSquare(position, self.constant["FIELD_GOAL_Y_TOP"], self.constant["FIELD_GOAL_Y_BOTTOM"],
                          x_left, x_right):
            if is_inside_circle(position, top_circle, self.constant["FIELD_GOAL_RADIUS"] + dist_from_goal_area):
                return True
            elif is_inside_circle(position, bot_circle, self.constant["FIELD_GOAL_RADIUS"] + dist_from_goal_area):
                return True
            return True
        else:
            return False

    def is_outside_goal_area(self, position, dist_from_goal_area=0, our_goal=True):
        return not self.is_inside_goal_area(position, dist_from_goal_area, our_goal)

    def stay_inside_goal_area(self, position, our_goal=True):
        if self.is_inside_goal_area(position, our_goal):
            return Position(position.x, position.y)
        else:
            x1 = self.constant["FIELD_OUR_GOAL_X_EXTERNAL"] if our_goal else self.constant["FIELD_THEIR_GOAL_X_EXTERNAL"]
            x2 = self.constant["FIELD_OUR_GOAL_X_INTERNAL"] if our_goal else self.constant["FIELD_THEIR_GOAL_X_INTERNAL"]

            x_right = max(x1, x2)
            x_left = min(x1, x2)

            position = stayInsideSquare(position, self.constant["FIELD_GOAL_Y_TOP"],
                                        self.constant["FIELD_GOAL_Y_BOTTOM"], x_left, x_right)
            if isInsideSquare(position, self.constant["FIELD_GOAL_Y_TOP"], self.constant["FIELD_GOAL_Y_BOTTOM"],
                              x_left, x_right):
                return position
            else:
                circle_top = self.constant["FIELD_OUR_GOAL_TOP_CIRCLE"] if our_goal\
                    else self.constant["FIELD_THEIR_GOAL_TOP_CIRCLE"]
                circle_bot = self.constant["FIELD_OUR_GOAL_BOTTOM_CIRCLE"] if our_goal\
                    else self.constant["FIELD_THEIR_GOAL_BOTTOM_CIRCLE"]
                dst_top = get_distance(circle_top, position)
                dst_bot = get_distance(circle_bot, position)

                if dst_top >= dst_bot:
                    return stayInsideCircle(position, circle_top, self.constant["FIELD_GOAL_RADIUS"])
                else:
                    return stayInsideCircle(position, circle_bot, self.constant["FIELD_GOAL_RADIUS"])

    def stay_outside_goal_area(self, position, dist_from_goal_area=200, our_goal=True):
        if self.is_outside_goal_area(position, dist_from_goal_area, our_goal):
            return Position(position.x, position.y)
        else:
            x1 = self.constant["FIELD_OUR_GOAL_X_EXTERNAL"] if our_goal else self.constant["FIELD_THEIR_GOAL_X_EXTERNAL"]
            x2 = self.constant["FIELD_OUR_GOAL_X_INTERNAL"] if our_goal else self.constant["FIELD_THEIR_GOAL_X_INTERNAL"]
            x1 = 2*x1-x2

            x_right = max(x1, x2) + dist_from_goal_area
            x_left = min(x1, x2) - dist_from_goal_area

            y_top = self.constant["FIELD_GOAL_SEGMENT"] / 2
            y_bottom = (self.constant["FIELD_GOAL_SEGMENT"] / 2) * -1

            circle_top = self.constant["FIELD_OUR_GOAL_TOP_CIRCLE"] if our_goal\
                else self.constant["FIELD_THEIR_GOAL_TOP_CIRCLE"]
            circle_bot = self.constant["FIELD_OUR_GOAL_BOTTOM_CIRCLE"] if our_goal\
                else self.constant["FIELD_THEIR_GOAL_BOTTOM_CIRCLE"]

            position = stayOutsideSquare(position, y_top, y_bottom, x_left, x_right)
            position = stayOutsideCircle(position, circle_top, self.constant["FIELD_GOAL_RADIUS"] + dist_from_goal_area)
            position = stayOutsideCircle(position, circle_bot, self.constant["FIELD_GOAL_RADIUS"] + dist_from_goal_area)
            return Position(position.x, position.y)

    def stay_inside_play_field(self, position):
        return stayInsideSquare(position, Y_TOP=self.constant["FIELD_Y_TOP"],
                                          Y_BOTTOM=self.constant["FIELD_Y_BOTTOM"],
                                          X_LEFT=self.constant["FIELD_X_LEFT"],
                                          X_RIGHT=self.constant["FIELD_X_RIGHT"])

    def stay_inside_full_field(self, position):
        return stayInsideSquare(position, Y_TOP=self.constant["FIELD_Y_TOP"] + self.constant["FIELD_BOUNDARY_WIDTH"],
                                Y_BOTTOM=self.constant["FIELD_Y_BOTTOM"] - self.constant["FIELD_BOUNDARY_WIDTH"],
                                X_LEFT=self.constant["FIELD_X_LEFT"] - self.constant["FIELD_BOUNDARY_WIDTH"],
                                X_RIGHT=self.constant["FIELD_X_RIGHT"] + self.constant["FIELD_BOUNDARY_WIDTH"])

    def respect_field_rules(self, position):
        new_position = self.stay_outside_goal_area(position, our_goal=False)
        return self.stay_inside_play_field(new_position)


    def update_field_dimensions(self, packets):
        for packet in packets:
            if not packet.HasField("geometry"):
                continue
            field = packet.geometry.field
            if len(field.field_lines) == 0:
                raise RuntimeError("Receiving legacy geometry message instead of the new geometry message. Update your grsim or check your vision port.")

            self.field_lines = self._convert_field_line_segments(field.field_lines)
            self.field_arcs = self._convert_field_circular_arc(field.field_arcs)

            if "RightFieldLeftPenaltyArc" not in self.field_arcs:
                # This is a new type of field for Robocup 2018, it does not have a circular goal zone
                self._defense_radius = self.field_lines["LeftFieldLeftPenaltyStretch"].length
            else:
                self._defense_radius = self.field_arcs['RightFieldLeftPenaltyArc'].radius


            self._field_length = field.field_length
            self._field_width = field.field_width
            self._boundary_width = field.boundary_width
            self._goal_width = field.goal_width
            self._goal_depth = field.goal_depth
            self._center_circle_radius = self.field_arcs['CenterCircle'].radius
            self._defense_stretch = 100 # hard coded parce que cette valeur d'est plus valide et que plusieurs modules en ont de besoin
            #la valeur qu'on avait apres le fix a Babin était de 9295 mm, ce qui est 90 fois la grandeur d'avant.

            self.constant["FIELD_Y_TOP"] = self._field_width / 2
            self.constant["FIELD_Y_BOTTOM"] = -self._field_width / 2
            self.constant["FIELD_X_LEFT"] = -self._field_length / 2
            self.constant["FIELD_X_RIGHT"] = self._field_length / 2

            self.constant["CENTER_CENTER_RADIUS"] = self._center_circle_radius

            self.constant["FIELD_Y_POSITIVE"] = self._field_width / 2
            self.constant["FIELD_Y_NEGATIVE"] = -self._field_width / 2
            self.constant["FIELD_X_NEGATIVE"] = -self._field_length / 2
            self.constant["FIELD_X_POSITIVE"] = self._field_length / 2

            self.constant["FIELD_BOUNDARY_WIDTH"] = self._boundary_width

            self.constant["FIELD_GOAL_RADIUS"] = self._defense_radius
            self.constant["FIELD_GOAL_SEGMENT"] = self._defense_stretch
            self.constant["FIELD_GOAL_WIDTH"] = self._goal_width

            self.constant["FIELD_GOAL_Y_TOP"] = self._defense_radius + (self._defense_stretch / 2)
            self.constant["FIELD_GOAL_Y_BOTTOM"] = -self.constant["FIELD_GOAL_Y_TOP"]


            if self.our_side == FieldSide.POSITIVE:
                self.constant["FIELD_THEIR_GOAL_X_EXTERNAL"] = self.constant["FIELD_X_NEGATIVE"]
                self.constant["FIELD_THEIR_GOAL_X_INTERNAL"] = self.constant["FIELD_X_NEGATIVE"] + self.constant["FIELD_GOAL_RADIUS"]

                self.constant["FIELD_OUR_GOAL_X_INTERNAL"] = self.constant["FIELD_X_POSITIVE"] - self.constant["FIELD_GOAL_RADIUS"]
                self.constant["FIELD_OUR_GOAL_X_EXTERNAL"] = self.constant["FIELD_X_POSITIVE"]

                self.constant["FIELD_THEIR_GOAL_TOP_CIRCLE"] = Position(self.constant["FIELD_X_NEGATIVE"], self.constant["FIELD_GOAL_SEGMENT"] / 2)
                self.constant["FIELD_THEIR_GOAL_BOTTOM_CIRCLE"] = Position(self.constant["FIELD_X_NEGATIVE"], -self.constant["FIELD_GOAL_SEGMENT"] / 2)
                self.constant["FIELD_THEIR_GOAL_MID_GOAL"] = Position(self.constant["FIELD_X_NEGATIVE"], 0)

                self.constant["FIELD_OUR_GOAL_TOP_CIRCLE"] = Position(self.constant["FIELD_X_POSITIVE"], self.constant["FIELD_GOAL_SEGMENT"] / 2)
                self.constant["FIELD_OUR_GOAL_BOTTOM_CIRCLE"] = Position(self.constant["FIELD_X_POSITIVE"], -self.constant["FIELD_GOAL_SEGMENT"] / 2)
                self.constant["FIELD_OUR_GOAL_MID_GOAL"] = Position(self.constant["FIELD_X_POSITIVE"], 0)

            else:
                self.constant["FIELD_OUR_GOAL_X_EXTERNAL"] = self.constant["FIELD_X_NEGATIVE"]
                self.constant["FIELD_OUR_GOAL_X_INTERNAL"] = self.constant["FIELD_X_NEGATIVE"] + self.constant["FIELD_GOAL_RADIUS"]

                self.constant["FIELD_THEIR_GOAL_X_INTERNAL"] = self.constant["FIELD_X_POSITIVE"] - self.constant["FIELD_GOAL_RADIUS"]
                self.constant["FIELD_THEIR_GOAL_X_EXTERNAL"] = self.constant["FIELD_X_POSITIVE"]

                self.constant["FIELD_OUR_GOAL_TOP_CIRCLE"] = Position(self.constant["FIELD_X_NEGATIVE"], self.constant["FIELD_GOAL_SEGMENT"] / 2)
                self.constant["FIELD_OUR_GOAL_BOTTOM_CIRCLE"] = Position(self.constant["FIELD_X_NEGATIVE"], -self.constant["FIELD_GOAL_SEGMENT"] / 2)
                self.constant["FIELD_OUR_GOAL_MID_GOAL"] = Position(self.constant["FIELD_X_NEGATIVE"], 0)

                self.constant["FIELD_THEIR_GOAL_TOP_CIRCLE"] = Position(self.constant["FIELD_X_POSITIVE"], self.constant["FIELD_GOAL_SEGMENT"] / 2)
                self.constant["FIELD_THEIR_GOAL_BOTTOM_CIRCLE"] = Position(self.constant["FIELD_X_POSITIVE"], -self.constant["FIELD_GOAL_SEGMENT"] / 2)
                self.constant["FIELD_THEIR_GOAL_MID_GOAL"] = Position(self.constant["FIELD_X_POSITIVE"], 0)

            self.set_collision_body()
            return True
        return False

    def _convert_field_circular_arc(self, field_arcs):
        result = {}
        for arc in field_arcs:
            result[arc.name] = FieldCircularArc(arc)
        return result

    def _convert_field_line_segments(self, field_lines):
        result = {}
        for line in field_lines:
            result[line.name] = FieldLineSegment(line)
        return result


positive_side_constant = {
    "ROBOT_RADIUS": 90,
    "BALL_RADIUS": 22,
    "PLAYER_PER_TEAM": 6,
    "KICK_MAX_SPD": 4,
    # Field Parameters
    "FIELD_Y_TOP": 3000,
    "FIELD_Y_BOTTOM": -3000,
    "FIELD_X_LEFT": -4500,
    "FIELD_X_RIGHT": 4500,

    "CENTER_CENTER_RADIUS": 1000,
    
    "FIELD_Y_POSITIVE": 3000,
    "FIELD_Y_NEGATIVE": -3000,
    "FIELD_X_NEGATIVE": -4500,
    "FIELD_X_POSITIVE": 4500,

    "FIELD_BOUNDARY_WIDTH": 700,
    
    "FIELD_GOAL_RADIUS": 1000,
    "FIELD_GOAL_SEGMENT": 500,

    # Goal Parameters
    "FIELD_GOAL_WIDTH": 1000,
    "FIELD_GOAL_Y_TOP": 1250,  # FIELD_GOAL_RADIUS + FIELD_GOAL_SEGMENT / 2
    "FIELD_GOAL_Y_BOTTOM": -1250,  # (FIELD_GOAL_RADIUS + FIELD_GOAL_SEGMENT / 2) * -1
    "FIELD_OUR_GOAL_X_EXTERNAL": 4500,  # FIELD_X_LEFT
    "FIELD_OUR_GOAL_X_INTERNAL": 3500,  # FIELD_X_LEFT + FIELD_GOAL_RADIUS
    "FIELD_THEIR_GOAL_X_INTERNAL": -3500,  # FIELD_X_RIGHT - FIELD_GOAL_RADIUS
    "FIELD_THEIR_GOAL_X_EXTERNAL": -4500,  # FIELD_X_RIGHT

    "FIELD_DEFENSE_PENALTY_MARK": Position(1, 0),
    "FIELD_OFFENSE_PENALTY_MARK": Position(1, 0),

    # Field Positions
    "FIELD_OUR_GOAL_TOP_CIRCLE": Position(4500, 250),  # FIELD_X_LEFT, FIELD_GOAL_SEGMENT / 2)
    "FIELD_OUR_GOAL_BOTTOM_CIRCLE": Position(4500, -250),  # FIELD_X_LEFT, FIELD_GOAL_SEGMENT / 2 * -1)
    "FIELD_OUR_GOAL_MID_GOAL": Position(4500, 0),
    "FIELD_THEIR_GOAL_TOP_CIRCLE": Position(-4500, 250),  # FIELD_X_RIGHT, FIELD_GOAL_SEGMENT / 2)
    "FIELD_THEIR_GOAL_BOTTOM_CIRCLE": Position(-4500, -250),  # FIELD_X_RIGHT, FIELD_GOAL_SEGMENT / 2 * -1)
    "FIELD_THEIR_GOAL_MID_GOAL": Position(-4500, 0),

    # Legal field dimensions
    "LEGAL_Y_TOP": 3000,
    "LEGAL_Y_BOTTOM": -3000,
    "LEGAL_X_LEFT": -4500,
    "LEGAL_X_RIGHT": 4500,
}

negative_side_constant = {
    "ROBOT_RADIUS": 90,
    "BALL_RADIUS": 22,
    "PLAYER_PER_TEAM": 6,
    "KICK_MAX_SPD": 4,

    # Field Parameters
    "FIELD_Y_TOP": 3000,
    "FIELD_Y_BOTTOM": -3000,
    "FIELD_X_LEFT": -4500,
    "FIELD_X_RIGHT": 4500,

    "CENTER_CENTER_RADIUS": 1000,
    
    "FIELD_Y_POSITIVE": 3000,
    "FIELD_Y_NEGATIVE": -3000,
    "FIELD_X_NEGATIVE": -4500,
    "FIELD_X_POSITIVE": 4500,
    
    "FIELD_GOAL_RADIUS": 1000,
    "FIELD_GOAL_SEGMENT": 500,


    # Goal Parameters
    "FIELD_GOAL_WIDTH": 1000,
    "FIELD_GOAL_Y_TOP": 1250,  # FIELD_GOAL_RADIUS + FIELD_GOAL_SEGMENT / 2
    "FIELD_GOAL_Y_BOTTOM": -1250,  # (FIELD_GOAL_RADIUS + FIELD_GOAL_SEGMENT / 2) * -1
    "FIELD_OUR_GOAL_X_EXTERNAL": -4500,  # FIELD_X_LEFT
    "FIELD_OUR_GOAL_X_INTERNAL": -3500,  # FIELD_X_LEFT + FIELD_GOAL_RADIUS
    "FIELD_THEIR_GOAL_X_INTERNAL": 3500,  # FIELD_X_RIGHT - FIELD_GOAL_RADIUS
    "FIELD_THEIR_GOAL_X_EXTERNAL": 4500,  # FIELD_X_RIGHT

    "FIELD_DEFENSE_PENALTY_MARK": Position(1, 0),
    "FIELD_OFFENSE_PENALTY_MARK": Position(1, 0),

    # Field Positions
    "FIELD_OUR_GOAL_TOP_CIRCLE": Position(-4500, 250),  # FIELD_X_LEFT, FIELD_GOAL_SEGMENT / 2)
    "FIELD_OUR_GOAL_BOTTOM_CIRCLE": Position(-4500, -250),  # FIELD_X_LEFT, FIELD_GOAL_SEGMENT / 2 * -1)
    "FIELD_OUR_GOAL_MID_GOAL": Position(-4500, 0),
    "FIELD_THEIR_GOAL_TOP_CIRCLE": Position(4500, 250),  # FIELD_X_RIGHT, FIELD_GOAL_SEGMENT / 2)
    "FIELD_THEIR_GOAL_BOTTOM_CIRCLE": Position(4500, -250),  # FIELD_X_RIGHT, FIELD_GOAL_SEGMENT / 2 * -1)
    "FIELD_THEIR_GOAL_MID_GOAL": Position(4500, 0),


    # Legal field dimensions
    "LEGAL_Y_TOP": 3000,
    "LEGAL_Y_BOTTOM": -3000,
    "LEGAL_X_LEFT": -4500,
    "LEGAL_X_RIGHT": 4500,
}
