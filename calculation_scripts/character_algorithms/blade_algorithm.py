"""Module containing a specific algorithm for Blade."""

from typing import Callable
from character_utils.characters import CharStats
from ..detailed_breakdown import print_detailed_breakdown
from gui_scripts.user_input import UserInput
from equipment_utils.support_light_cones import apply_support_lcs
from calculation_scripts.rotation import RotationList
from calculation_scripts.calculations_utils import (
    find_best_rotation, print_char_info, calculate_turn_energy,
    print_er_breakpoint, print_rotation_info)


def dfs_algorithm_blade(stats: CharStats, user_input: UserInput) -> RotationList:
    """Blade possesses the ability to use enhanced basic attacks that generate more energy.
    Skill grants 3 charges for these attacks, and does not end turn.
    Additionally he can perform follow-up attacks which cost 5 stacks (4 with Eidolon 6).
    These stacks are gained by attacking, using skills, using ultimates, or being attacked."""

    follow_up_cost, blade_stacks = _prep_init_stats(user_input)
    all_rotations = RotationList()
    stack = [(stats.init_energy, [], 0, 0, blade_stacks)]

    while stack:
        curr_energy, turns, skill_points_generated, e_basic_charges, blade_stacks = stack.pop()

        if curr_energy >= stats.ult_cost:
            all_rotations.add_rotation(curr_energy, turns,
                                       skill_points_generated)
            continue

        blade_stacks = _gain_stacks(user_input, blade_stacks)
        curr_energy = apply_support_lcs(stats, user_input, curr_energy)
        curr_energy += calculate_turn_energy(user_input)

        # Blade has enough stacks for a follow-up attack
        if blade_stacks >= follow_up_cost:
            stack.append((curr_energy + stats.follow_up,
                          turns, skill_points_generated,
                          e_basic_charges, blade_stacks - follow_up_cost))

        # Blade uses skill that does not end his turn
        if e_basic_charges == 0:
            blade_stacks += 1
            e_basic_charges = 4
            skill_points_generated -= 1

        # Blade uses Enhanced Basic
        if e_basic_charges > 0:
            stack.append((curr_energy + stats.e_basic,
                          turns + ["E. BASIC"], skill_points_generated,
                          e_basic_charges - 1, blade_stacks + 1))

    return all_rotations


def _gain_stacks(user_input: UserInput, stacks: int) -> int:
    """Character gains stacks with every hit taken."""

    if user_input.hits_taken.repeat_every_turn:
        stacks += user_input.hits_taken.num_triggers

    elif user_input.hits_taken.num_triggers > 0:
        stacks += 1

    return stacks


def _prep_init_stats(user_input: UserInput) -> tuple[int, int]:
    follow_up_cost = 5
    if user_input.eidolon_level == 6:
        follow_up_cost -= 1

    blade_stacks = 1 * user_input.assume_ult + 1 * user_input.technique

    return follow_up_cost, blade_stacks


def print_results_blade(stats: CharStats, user_input: UserInput, rotations: RotationList,
                        algorithm: Callable[[CharStats, UserInput], RotationList]) -> None:
    """Specialized print function for Blade
    as his rotations include only enhanced basic attacks."""

    print_char_info(stats, user_input)

    best_rotation = find_best_rotation(rotations)
    print_rotation_info("Enchanted Basic rotation", best_rotation)
    print_er_breakpoint(find_best_rotation, algorithm, rotations,
                        best_rotation, stats, user_input,
                        stats.energy_recharge)

    print("\n")

    if user_input.detailed_breakdown:
        print_detailed_breakdown(stats, user_input, best_rotation)
