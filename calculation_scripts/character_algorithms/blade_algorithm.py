"""Module containing a specific algorithm for Blade."""

from termcolor import colored
from calculation_scripts.calculations_utils import (Rotation, get_char_info,
                                                    calculate_turn_energy, get_er_breakpoint)
from characters import CharStats
from gui_scripts.gui_utils import UserInput
from support_light_cones import apply_support_lcs


def dfs_algorithm_blade(stats: CharStats, user_input: UserInput) -> list[Rotation]:
    """Blade possesses the ability to use enhanced basic attacks that generate more energy.
    Skill grants 3 charges for these attacks, and does not end turn.
    Additionally he can perform follow-up attacks which cost 5 stacks (4 with Eidolon 6).
    These stacks are gained by attacking, using skills, using ultimates, or being attacked."""

    stats.e_basic = stats.basic + 10 * stats.energy_recharge
    curr_energy = stats.init_energy

    follow_up_cost = 5
    if user_input.eidolons == 6:
        follow_up_cost -= 1

    skill_points_generated = 0
    e_basic_charges = 0
    blade_stacks = 1 * user_input.assume_ult + 1 * user_input.technique

    all_rotations: list[Rotation] = []
    stack: list = [(curr_energy, all_rotations,
                    skill_points_generated, e_basic_charges, blade_stacks)]

    while stack:
        curr_energy, turns, skill_points_generated, e_basic_charges, blade_stacks = stack.pop()

        if curr_energy >= stats.ult_cost:
            rotation = Rotation(curr_energy, turns, skill_points_generated)
            all_rotations.append(rotation)
            continue

        # Blade has enough stacks for a follow-up attack
        if blade_stacks >= follow_up_cost:
            stack.append((curr_energy + stats.follow_up,
                          turns, skill_points_generated, e_basic_charges,
                          blade_stacks - follow_up_cost))

        if user_input.num_hits_taken == "every turn" or user_input.num_hits_taken > 0:
            blade_stacks += 1

        curr_energy = apply_support_lcs(stats, user_input, curr_energy)
        turn_energy = calculate_turn_energy(stats, user_input)

        # Blade uses skill that does not end his turn
        if e_basic_charges == 0:
            stack.append((curr_energy, turns, skill_points_generated - 1,
                          e_basic_charges + 3, blade_stacks + 1))

        # Blade uses Enhanced Basic
        if e_basic_charges > 0:
            stack.append((curr_energy + stats.e_basic + turn_energy,
                          turns + ["E. BASIC"], skill_points_generated,
                          e_basic_charges - 1, blade_stacks + 1))

    return all_rotations


def print_results_blade(stats: CharStats,
                        user_input: UserInput, rotations: list[Rotation]) -> Rotation:
    """Specialized print function for Blade
    as his rotations include only enhanced basic attacks."""

    char_info = get_char_info(stats.energy_recharge, user_input)
    print(colored(char_info, "green"))

    rotation = min(rotations,
                   key=lambda r: (r.num_turns, -r.skill_point_generated))

    er_breakpoint = get_er_breakpoint(rotation, stats.e_basic,
                                      stats.ult_cost, stats.init_energy)

    print(f"Enchanted Basic rotation ({rotation.energy_generated} energy, "
          f"{rotation.sp_cost_per_turn} SP/turn): {rotation.turn_sequence}")
    print(f"ER needed for the next breakpoint: {er_breakpoint}%\n")

    return rotation
