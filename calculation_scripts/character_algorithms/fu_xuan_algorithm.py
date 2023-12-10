"""This module contains a specific algorithm for Fu Xuan."""

from characters import CharStats
from gui_scripts.user_input import UserInput
from support_light_cones import apply_support_lcs
from calculation_scripts.rotation import RotationList
from calculation_scripts.calculations_utils import calculate_turn_energy


def dfs_algorithm_fx(stats: CharStats, user_input: UserInput) -> RotationList:
    """Fu Xuan's skill creates a matrix field for 3 turns.
    Using another skill during this time will generate additional energy."""

    matrix_duration = _prep_init_stats(stats, user_input)
    all_rotations = RotationList()
    stack = [(stats.init_energy, [], 0, matrix_duration)]

    while stack:
        curr_energy, turns, skill_points_generated, matrix_duration = stack.pop()

        if curr_energy >= stats.ult_cost:
            all_rotations.add_rotation(curr_energy, turns,
                                       skill_points_generated)
            continue

        curr_energy = apply_support_lcs(stats, user_input, curr_energy)
        turn_energy = calculate_turn_energy(stats, user_input)

        # Fu Xuan uses Skill
        if matrix_duration == 0:
            new_matrix_duration = 3
            stack.append((curr_energy + stats.skill + turn_energy,
                          turns + ["SKILL"],
                          skill_points_generated - 1,
                          new_matrix_duration))

        # Fu Xuan uses Enhanced Skill
        elif matrix_duration > 0:
            new_matrix_duration = 3
            stack.append((curr_energy + stats.e_skill + turn_energy,
                          turns + ["E. SKILL"],
                          skill_points_generated - 1,
                          new_matrix_duration))

        # Fu Xuan uses Basic attack
        stack.append((curr_energy + stats.basic + turn_energy,
                      turns + ["BASIC"],
                      skill_points_generated + 1,
                      matrix_duration - 1))

    return all_rotations


def _prep_init_stats(stats: CharStats, user_input: UserInput) -> int:
    stats.e_skill = stats.skill + 20 * stats.energy_recharge
    matrix_duration = 2 if user_input.technique else 0

    return matrix_duration
