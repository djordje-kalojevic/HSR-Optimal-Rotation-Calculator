"""This module contains a specific algorithm for Arlan."""

from characters import CharStats
from gui_scripts.user_input import UserInput
from support_light_cones import apply_support_lcs
from calculation_scripts.calculations_utils import Rotation, calculate_turn_energy


def dfs_algorithm_arlan(stats: CharStats, user_input: UserInput) -> list[Rotation]:
    """Arlan does not use Skill Points for his skill."""

    all_rotations: list[Rotation] = []
    stack = [(stats.init_energy, [], 0)]

    while stack:
        curr_energy, turns, skill_points_generated = stack.pop()

        if curr_energy >= stats.ult_cost:
            rotation = Rotation(curr_energy, turns, skill_points_generated)
            all_rotations.append(rotation)
            continue

        curr_energy = apply_support_lcs(stats, user_input, curr_energy)
        turn_energy = calculate_turn_energy(stats, user_input)

        # Character uses Basic Attack
        stack.append((curr_energy + stats.basic + turn_energy,
                     turns + ["BASIC"], skill_points_generated + 1))

        # Character uses Skill
        stack.append((curr_energy + stats.skill + turn_energy,
                     turns + ["SKILL"], skill_points_generated))

    return all_rotations
