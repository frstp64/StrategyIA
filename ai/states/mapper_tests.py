from unittest import TestCase
from ..Util.role import Role
from .game_state import GameState

class RoleMapperTests(TestCase):
    def test_givenNoMapping_whenMapById_thenMapsAllPlayers(self):
        state = GameState()
        state.map_players_to_roles_by_id(basic_roles)
        self.assertDictEqual(state.get_role_mapping(), basic_roles)

    def test_givenBasicMapping_whenMapOtherwise_thenMapsPlayersProperly(self):
        state = GameState()
        state.map_players_to_roles_by_id(basic_roles)
        state.map_players_to_roles_by_id(inverted_roles_no_goal)
        self.assertDictEqual(state.get_role_mapping(), inverted_roles_no_goal)

    def test_givenBasicMapping_whenMapFewerRobots_thenRemovesUnasignedOnes(self):
        state = GameState()
        state.map_players_to_roles_by_id(basic_roles)
        state.map_players_to_roles_by_id(missing_middle)
        self.assertDictEqual(state.get_role_mapping(), missing_middle)

    def test_givenBasicMapping_whenMapMissingLockedRole_thenKeepsLockedRole(self):
        state = GameState()
        state.map_players_to_roles_by_id(basic_roles)
        state.map_players_to_roles_by_id(missing_required)
        self.assertDictEqual(state.get_role_mapping(), missing_required_expected)

    def test_givenBasicMapping_whenRemapLockedRole_thenThrowsValueError(self):
        state = GameState()
        state.map_players_to_roles_by_id(basic_roles)
        with self.assertRaises(ValueError):
            state.map_players_to_roles_by_id(inverted_roles)


basic_roles = {
    Role.GOALKEEPER: 0,
    Role.FIRST_DEFENCE: 1,
    Role.SECOND_DEFENCE: 2,
    Role.MIDDLE: 3,
    Role.FIRST_ATTACK: 4,
    Role.SECOND_ATTACK: 5
}

inverted_roles = {
    Role.GOALKEEPER: 5,
    Role.FIRST_DEFENCE: 4,
    Role.SECOND_DEFENCE: 3,
    Role.MIDDLE: 2,
    Role.FIRST_ATTACK: 1,
    Role.SECOND_ATTACK: 0
}

inverted_roles_no_goal = {
    Role.FIRST_DEFENCE: 4,
    Role.SECOND_DEFENCE: 3,
    Role.MIDDLE: 2,
    Role.FIRST_ATTACK: 1,
    Role.SECOND_ATTACK: 5,
    Role.GOALKEEPER: 0
}

missing_middle = {
    Role.GOALKEEPER: 0,
    Role.FIRST_DEFENCE: 1,
    Role.SECOND_DEFENCE: 2,
    Role.FIRST_ATTACK: 4,
    Role.SECOND_ATTACK: 5
}

missing_required = {
    Role.MIDDLE: 3,
    Role.FIRST_DEFENCE: 1,
    Role.SECOND_DEFENCE: 2,
    Role.FIRST_ATTACK: 5,
    Role.SECOND_ATTACK: 4
}

missing_required_expected = {
    Role.MIDDLE: 3,
    Role.FIRST_DEFENCE: 1,
    Role.SECOND_DEFENCE: 2,
    Role.FIRST_ATTACK: 5,
    Role.SECOND_ATTACK: 4,
    Role.GOALKEEPER: 0
}





