"""This module contains a default Depth-First Search algorithm
for characters that do not have a specialized one."""

from typing import Callable
from character_utils.characters import CharStats
from ..detailed_breakdown import print_detailed_breakdown
from gui_scripts.user_input import UserInput
from equipment_utils.support_light_cones import apply_support_lcs
from calculation_scripts.rotation import RotationList
from calculation_scripts.calculations_utils import (
    calculate_turn_energy, find_basic_only_rotation,
    find_best_rotation,
    find_neutral_rotation, find_one_skill_rotation,
    find_skill_only_rotation, print_char_info,
    print_rotation_info, print_er_breakpoint)


def dfs_algorithm_default(stats: CharStats, user_input: UserInput) -> RotationList:
    """Default Depth-First Search algorithm that determines
    the shortest and most skill-point positive rotation.
    Positive rotations are defined as those that use more basic attacks than skills,
    as the former generate skill points, and the latter consume them."""

    all_rotations = RotationList()
    stack = [(stats.init_energy, [], stats.init_sp)]

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
                     skill_points_generated - 1))

    return all_rotations


def print_results_default(stats: CharStats, user_input: UserInput, all_rotations: RotationList, algorithm: Callable):
    """Prints various rotation results, for example, the following:
        - character info: their name, energy recharge,
        Light Cone that's equipped and its superimposition
        - basic only rotation,
        and additional energy recharge needed to shorten th rotation by 1 turn
        - skill only rotation,
        and additional energy recharge needed to shorten this rotation by 1 turn
        - one skill rotation,
        useful for buffers/debuffers to see if rotation coincides with buff/debuff duration
        - Shortest, most skill-positive rotation, i.e.,
        it prioritizes rotations with the lowest skill point cost
        if multiple rotations are eligible."""

    print_char_info(stats, user_input)

    best_rotation = find_best_rotation(all_rotations)
    print_rotation_info("Most optimal rotation", best_rotation)
    print_er_breakpoint(find_best_rotation, algorithm, all_rotations,
                        best_rotation, stats, user_input,
                        stats.energy_recharge)

    neutral_rotation = find_neutral_rotation(all_rotations)
    print_rotation_info("Neutral rotation", neutral_rotation)
    print_er_breakpoint(find_neutral_rotation, algorithm, all_rotations,
                        neutral_rotation, stats, user_input,
                        stats.energy_recharge)

    basic_only_rot = find_basic_only_rotation(all_rotations)
    if basic_only_rot:
        print_rotation_info("Basic only rotation", basic_only_rot)
        print_er_breakpoint(find_basic_only_rotation, algorithm, all_rotations,
                            basic_only_rot, stats, user_input,
                            stats.energy_recharge)

    skill_only_rot = find_skill_only_rotation(all_rotations)
    if skill_only_rot:
        print_rotation_info("Skill only rotation", skill_only_rot)
        print_er_breakpoint(find_skill_only_rotation, algorithm, all_rotations,
                            skill_only_rot, stats, user_input,
                            stats.energy_recharge)

    one_skill_rot = find_one_skill_rotation(all_rotations)
    print_rotation_info("One skill rotation", one_skill_rot)
    print_er_breakpoint(find_one_skill_rotation, algorithm, all_rotations,
                        one_skill_rot, stats, user_input,
                        stats.energy_recharge)

    print("\n")

    if user_input.detailed_breakdown:
        print_detailed_breakdown(stats, user_input, best_rotation)
