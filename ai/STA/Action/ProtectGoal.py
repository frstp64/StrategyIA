# Under MIT licence, see LICENCE.txt
from Util import Pose, Position, AICommand
from Util.area import stayInsideCircle
from Util.geometry import closest_point_on_segment
from ai.GameDomainObjects import Player
from ai.STA.Action import Action
from ai.states.game_state import GameState


class ProtectGoal(Action):
    """
    Action ProtectGoal: Action de base pour le gardien de but. Déplace le gardien entre la balle et le centre du but, à
    une certaine distance de celui-ci, tout en restant dans la zone du gardien.
    Méthodes:
        exec(self): Retourne la pose où se rendre.
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du gardien.
        is_right_goal : Un booléen indiquant si le but à protéger est celui de droite.
        minimum_distance : La distance minimale qu'il doit y avoir entre le gardien et le centre du but.
        maximum_distance : La distance maximale qu'il doit y avoir entre le gardien et le centre du but.
    """
    def __init__(self, game_state: GameState, player: Player, is_right_goal: bool=True,
                 minimum_distance: [int, float]=150 / 2, maximum_distance: [int, float, None]=None):
        """
        :param game_state: L'état courant du jeu.
        :param player: L'instance du joueur qui est le gardien de but.
        :param is_right_goal: Un booléen indiquant si le but à protéger est celui de droite.
        :param minimum_distance: La distance minimale qu'il doit y avoir entre le gardien et le centre du but.
        :param maximum_distance: La distance maximale qu'il doit y avoir entre le gardien et le centre du but.
        """
        Action.__init__(self, game_state, player)
        assert isinstance(is_right_goal, bool)
        assert isinstance(minimum_distance, (int, float))
        assert (isinstance(maximum_distance, (int, float)) or maximum_distance is None)
        if maximum_distance is not None:
            assert maximum_distance >= minimum_distance
        if maximum_distance is None:
            maximum_distance = minimum_distance
        self.is_right_goal = is_right_goal
        self.minimum_distance = minimum_distance
        self.maximum_distance = maximum_distance

    def exec(self):
        """
        Calcul la pose que doit prendre le gardien en fonction de la position de la balle.
        :return: Un tuple (Pose, kick) où Pose est la destination du gardien et kick est nul (on ne botte pas)
        """
        goalkeeper_position = self.player.pose.position
        ball_position = self.game_state.ball_position
        goal_x = self.game_state.const["FIELD_OUR_GOAL_X_EXTERNAL"]
        goal_position = Position(goal_x, 0)

        # Calcul des deux positions extremums entre la balle et le centre du but
        inner_circle_position = stayInsideCircle(ball_position, goal_position, self.minimum_distance)
        outer_circle_position = stayInsideCircle(ball_position, goal_position, self.maximum_distance)

        destination_position = closest_point_on_segment(goalkeeper_position,
                                                        inner_circle_position,
                                                        outer_circle_position)

        # Vérification que destination_position respecte la distance maximale
        if self.maximum_distance is None:
            destination_position = self.game_state.game.field.stay_inside_goal_area(destination_position,
                                                                                    our_goal=True)
        else:
            destination_position = stayInsideCircle(destination_position, goal_position, self.maximum_distance)

        # Calcul de l'orientation de la pose de destination
        destination_orientation = (ball_position - destination_position).angle

        destination_pose = Pose(destination_position, destination_orientation)
        return AICommand(self.player.id, target=destination_pose.to_dict())
