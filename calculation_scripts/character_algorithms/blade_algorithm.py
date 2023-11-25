"""Module containing a specific algorithm for Blade."""

from characters import CharStats
from ..detailed_breakdown import print_detailed_breakdown
from gui_scripts.user_input import UserInput
from support_light_cones import apply_support_lcs
from calculation_scripts.calculations_utils import (
    Rotation, find_best_rotation,
    print_char_info, calculate_turn_energy,
    print_er_threshold, print_rotation_info)


def dfs_algorithm_blade(stats: CharStats, user_input: UserInput) -> list[Rotation]:
    """Blade possesses the ability to use enhanced basic attacks that generate more energy.
    Skill grants 3 charges for these attacks, and does not end turn.
    Additionally he can perform follow-up attacks which cost 5 stacks (4 with Eidolon 6).
    These stacks are gained by attacking, using skills, using ultimates, or being attacked."""

    follow_up_cost, blade_stacks = _prep_init_stats(stats, user_input)
    all_rotations: list[Rotation] = []
    stack = [(stats.init_energy, [], 0, 0, blade_stacks)]

    while stack:
        curr_energy, turns, skill_points_generated, e_basic_charges, blade_stacks = stack.pop()

        if curr_energy >= stats.ult_cost:
            rotation = Rotation(curr_energy, turns, skill_points_generated)
            all_rotations.append(rotation)
            continue

        blade_stacks = _gain_stacks(user_input, blade_stacks)
        curr_energy = apply_support_lcs(stats, user_input, curr_energy)
        turn_energy = calculate_turn_energy(stats, user_input)

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
            stack.append((curr_energy + stats.e_basic + turn_energy,
                          turns + ["E. BASIC"], skill_points_generated,
                          e_basic_charges - 1, blade_stacks + 1))

    return all_rotations


def _gain_stacks(user_input: UserInput, stacks: int) -> int:
    """Character gains stacks with every hit taken."""

    if user_input.num_hits_taken.repeat_every_turn:
        stacks += user_input.num_hits_taken.num_triggers

    elif user_input.num_hits_taken.num_triggers > 0:
        stacks += 1

    return stacks


def _prep_init_stats(stats: CharStats, user_input: UserInput) -> int:
    stats.e_basic = stats.basic + 10 * stats.energy_recharge

    follow_up_cost = 5
    if user_input.eidolon_level == 6:
        follow_up_cost -= 1

    blade_stacks = 1 * user_input.assume_ult + 1 * user_input.technique

    return follow_up_cost, blade_stacks


def print_results_blade(stats: CharStats, user_input: UserInput, rotations: list[Rotation]):
    """Specialized print function for Blade
    as his rotations include only enhanced basic attacks."""

    print_char_info(stats.energy_recharge, user_input)

    best_rotation = find_best_rotation(rotations)
    print_rotation_info("Enchanted Basic rotation", best_rotation)
    print_er_threshold(best_rotation, stats.e_basic,
                       stats.ult_cost, stats.init_energy)
    print("\n")

    if user_input.detailed_breakdown:
        print_detailed_breakdown(stats, user_input, best_rotation)
