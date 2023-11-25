"""This module contains a default Depth-First Search algorithm
for characters that do not have a specialized one."""

from characters import CharStats
from ..detailed_breakdown import print_detailed_breakdown
from gui_scripts.user_input import UserInput
from support_light_cones import apply_support_lcs
from calculation_scripts.calculations_utils import (
    Rotation, calculate_turn_energy,
    find_basic_only_rotation, find_best_rotation,
    find_neutral_rotation, find_one_skill_rotation,
    find_skill_only_rotation, print_char_info,
    print_er_threshold, print_rotation_info)


def dfs_algorithm_default(stats: CharStats, user_input: UserInput) -> list[Rotation]:
    """Default Depth-First Search algorithm that determines
    the shortest and most skill-point positive rotation.
    Positive rotations are defined as those that use more basic attacks than skills,
    as the former generate skill points, and the latter consume them."""

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
                     turns + ["SKILL"], skill_points_generated - 1))

    return all_rotations


def print_results_default(stats: CharStats, user_input: UserInput, all_rotations: list[Rotation]):
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

    print_char_info(stats.energy_recharge, user_input)

    best_rotation = find_best_rotation(all_rotations)
    print_rotation_info("Most optimal rotation", best_rotation)

    neutral_rotation = find_neutral_rotation(all_rotations)
    print_rotation_info("Neutral rotation", neutral_rotation)

    basic_only_rot = find_basic_only_rotation(all_rotations)
    if basic_only_rot:
        print_rotation_info("Basic only rotation", basic_only_rot)
        print_er_threshold(basic_only_rot, stats.basic,
                           stats.ult_cost, stats.init_energy)

    skill_only_rot = find_skill_only_rotation(all_rotations)
    if skill_only_rot:
        print_rotation_info("Skill only rotation", skill_only_rot)
        print_er_threshold(skill_only_rot, stats.skill,
                           stats.ult_cost, stats.init_energy)

    one_skill_rot = find_one_skill_rotation(all_rotations)
    print_rotation_info("One skill rotation", one_skill_rot)

    print("\n")

    if user_input.detailed_breakdown:
        print_detailed_breakdown(stats, user_input, best_rotation)
