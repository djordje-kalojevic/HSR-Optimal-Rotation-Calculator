"""This module contains a default Depth-First Search algorithm
for characters that do not have a specialized one."""

from termcolor import colored
from calculation_scripts.calculations_utils import (
    Rotation, calculate_turn_energy,
    find_basic_only_rotation, find_best_rotation,
    find_neutral_rotation, find_one_skill_rotation,
    find_skill_only_rotation, get_char_info, get_er_breakpoint)
from characters import CharStats
from gui_scripts.gui_utils import UserInput
from support_light_cones import apply_support_lcs


def dfs_algorithm_default(stats: CharStats, user_input: UserInput) -> list[Rotation]:
    """Default Depth-First Search algorithm that determines
    the shortest and most skill-point positive rotation.
    Positive rotations are defined as those that use more basic attacks than skills,
    as the former generate skill points, and the latter consume them."""

    curr_energy = stats.init_energy
    skill_points_generated = 0
    all_rotations: list[Rotation] = []
    stack: list = [(curr_energy, all_rotations, skill_points_generated)]

    while stack:
        curr_energy, turns, skill_points_generated = stack.pop()

        if curr_energy >= stats.ult_cost:
            rotation = Rotation(curr_energy, turns, skill_points_generated)
            all_rotations.append(rotation)
            continue

        curr_energy = apply_support_lcs(stats, user_input, curr_energy)
        turn_energy = calculate_turn_energy(stats, user_input)

        stack.append((curr_energy + stats.basic + turn_energy,
                     turns + ["BASIC"], skill_points_generated + 1))
        stack.append((curr_energy + stats.skill + turn_energy,
                     turns + ["SKILL"], skill_points_generated - 1))

    return all_rotations


def print_results(stats: CharStats, user_input: UserInput,
                  all_rotations: list[Rotation]) -> Rotation:
    """Prints to the console the following:
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

    char_info = get_char_info(stats.energy_recharge, user_input)
    print(colored(char_info, "green"))

    best_rotation = find_best_rotation(all_rotations)
    if best_rotation:
        print(f"Most optimal rotation ({best_rotation.energy_generated} energy, "
              f"{best_rotation.sp_cost_per_turn} SP/T): {best_rotation.turn_sequence}")

    neutral_rotation = find_neutral_rotation(all_rotations)
    if neutral_rotation:
        print(f"Neutral rotation ({neutral_rotation.energy_generated} energy): "
              f"{neutral_rotation.turn_sequence}")

    basic_only_rotation = find_basic_only_rotation(all_rotations)
    if basic_only_rotation:
        basic_er_threshold = get_er_breakpoint(basic_only_rotation, stats.basic,
                                               stats.ult_cost, stats.init_energy)
        print(f"Basic only rotation ({basic_only_rotation.energy_generated} energy): "
              f"{basic_only_rotation.turn_sequence}")
        print(f"ER needed for the next breakpoint: {basic_er_threshold}%")

    skill_only_rotation = find_skill_only_rotation(all_rotations)
    if skill_only_rotation:
        skill_er_threshold = get_er_breakpoint(skill_only_rotation, stats.skill,
                                               stats.ult_cost, stats.init_energy)
        print(f"Skill only rotation ({skill_only_rotation.energy_generated} energy): "
              f"{skill_only_rotation.turn_sequence}")
        print(f"ER needed for the next breakpoint: {skill_er_threshold}%")

    one_skill_rotation = find_one_skill_rotation(all_rotations)
    if one_skill_rotation:
        print(f"One skill rotation ({one_skill_rotation.energy_generated} energy, "
              f"{one_skill_rotation.sp_cost_per_turn} SP/T): "
              f"{one_skill_rotation.turn_sequence}\n")

    return best_rotation
