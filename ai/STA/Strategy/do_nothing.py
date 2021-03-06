# Under MIT License, see LICENSE.txt
from Util.role import Role
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.stop import Stop


# noinspection PyTypeChecker
class DoNothing(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        for r in Role:
            p = self.game_state.get_player_by_role(r)
            if p is None:
                continue
            self.add_tactic(r, Stop(self.game_state, p))
