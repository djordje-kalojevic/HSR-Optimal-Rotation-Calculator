"""This module contains a specific algorithm for Arlan."""

from character_utils.characters import CharStats
from gui_scripts.user_input import UserInput
from equipment_utils.support_light_cones import apply_support_lcs
from calculation_scripts.rotation import RotationList
from calculation_scripts.calculations_utils import calculate_turn_energy


def dfs_algorithm_arlan(stats: CharStats, user_input: UserInput) -> RotationList:
    """Arlan does not use Skill Points for his skill."""

    all_rotations = RotationList()
    stack = [(stats.init_energy, [], 0)]

    while stack:
        curr_energy, turns, skill_points_generated = stack.pop()

        if curr_energy >= stats.ult_cost:
            all_rotations.add_rotation(curr_energy, turns,
                                       skill_points_generated)
            continue

        curr_energy = apply_support_lcs(stats, user_input, curr_energy)
        curr_energy += calculate_turn_energy(user_input)

        # Character uses Basic Attack
        stack.append((curr_energy + stats.basic,
                     turns + ["BASIC"],
                     skill_points_generated + 1))

        # Character uses Skill
        stack.append((curr_energy + stats.skill,
                     turns + ["SKILL"],
                     skill_points_generated))

    return all_rotations
