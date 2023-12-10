"""This module contains a specific algorithm for Dan Heng Imbibitor Lunae (DHIL)."""

from characters import CharStats
from support_light_cones import apply_support_lcs
from gui_scripts.user_input import UserInput
from ..detailed_breakdown import print_detailed_breakdown
from calculation_scripts.rotation import Rotation, RotationList
from calculation_scripts.calculations_utils import (calculate_turn_energy,
                                                    print_char_info, print_rotation_info)


def dfs_algorithm_dhil(stats: CharStats, user_input: UserInput) -> RotationList:
    """Dan Heng Imbibitor Lunae, or DHIL for short,
    possesses the ability to use 3 levels of enhanced basic attacks
    which generate more energy (30, 35, 40 respectively).
    Their costs are 1, 2, and 3 skill points respectively.
    Additionally, DHIL can get stacks through the use of his ultimate or technique
    these stacks can be used instead of regular Skill Points."""

    skill_points_generated = _prep_init_stats(stats, user_input)
    all_rotations = RotationList()
    stack = [(stats.init_energy, [], skill_points_generated)]

    while stack:
        curr_energy, turns, skill_points_generated = stack.pop()

        if curr_energy >= stats.ult_cost:
            all_rotations.add_rotation(curr_energy, turns,
                                       skill_points_generated)
            continue

        curr_energy = apply_support_lcs(stats, user_input, curr_energy)
        turn_energy = calculate_turn_energy(stats, user_input)

        # DHIL uses Basic Attack
        stack.append((curr_energy + stats.basic + turn_energy,
                      turns + ["BASIC"], skill_points_generated + 1))

        # DHIL uses Enhanced Attack 1
        stack.append((curr_energy + stats.e_basic + turn_energy,
                      turns + ["EB1"], skill_points_generated - 1))

        # DHIL uses Enhanced Attack 2
        stack.append((curr_energy + stats.e_basic_2 + turn_energy,
                      turns + ["EB2"], skill_points_generated - 2))

        # DHIL uses Enhanced Attack 3
        stack.append((curr_energy + stats.e_basic_3 + turn_energy,
                      turns + ["EB3"], skill_points_generated - 3))

    return all_rotations


def _prep_init_stats(stats: CharStats, user_input: UserInput) -> int:
    stats.e_basic = stats.basic + 10 * stats.energy_recharge
    stats.e_basic_2 = stats.basic + 15 * stats.energy_recharge
    stats.e_basic_3 = stats.basic + 20 * stats.energy_recharge

    skill_points_generated = 0 + 2 * user_input.assume_ult + 1 * user_input.technique
    if user_input.assume_ult and user_input.eidolon_level >= 2:
        skill_points_generated += 1

    return skill_points_generated


def print_results_dhil(stats: CharStats, user_input: UserInput,
                       all_rotations: RotationList) -> None:
    """Prints DHIL's various rotations. This includes his best, most effective rotation,
    as well as rotations with various skill point breakpoints.
    Such breakpoints include -0.5, -1.25, -1.5, -2, and -2.33 skill points per turn (SP/T)."""

    print_char_info(stats, user_input)

    best_rotation = min(all_rotations, key=_get_best_rotation_sorting_key)
    print_rotation_info("Best rotation", best_rotation)

    print_dhil_rotation(all_rotations, sp_cost_per_turn=0)
    print_dhil_rotation(all_rotations, sp_cost_per_turn=-0.5)
    print_dhil_rotation(all_rotations, sp_cost_per_turn=-1.25)
    print_dhil_rotation(all_rotations, sp_cost_per_turn=-1.5)
    print_dhil_rotation(all_rotations, sp_cost_per_turn=-2)
    print_dhil_rotation(all_rotations, sp_cost_per_turn=-2.33)

    print("\n")

    if user_input.detailed_breakdown:
        print_detailed_breakdown(stats, user_input, best_rotation)


def print_dhil_rotation(all_rotations: RotationList, sp_cost_per_turn: float) -> None:
    """Prints the best DHIL's rotation with the specified Skill Point cost per turn, or less."""

    rotation = min((r for r in all_rotations
                    if r.sp_cost_per_turn >= sp_cost_per_turn),
                   key=lambda r: _get_best_general_sorting_key(r))

    if sp_cost_per_turn == 0:
        rotation_name = "Neutral rotation"
    else:
        rotation_name = f"{sp_cost_per_turn} SP/T rotation"

    print_rotation_info(rotation_name, rotation, False)


def _get_best_rotation_sorting_key(rotation: Rotation) -> tuple:
    """Dan Heng Imbibitor Lunae's rotations are sorted by the following criteria:
    their length, their skill point cost, and the number of his various attacks.
    This ensures a short, efficient rotation,
    that still favours damage potential where possible."""

    sorting_key = (rotation.num_turns, -rotation.sp_cost_per_turn,
                   -rotation.turns.count("EB3"), -rotation.turns.count("EB2"),
                   -rotation.turns.count("EB1"), -rotation.turns.count("BASIC"))

    return sorting_key


def _get_best_general_sorting_key(rotation: Rotation) -> tuple:
    """Dan Heng Imbibitor Lunae's (DHIL) rotations are sorted by the following criteria:
    their length, their skill point cost, and the number of his various attacks.
    This ensures a short rotation of specific skill point (SP) cost,
    that still favours damage potential where possible.
    This is important as DHIL's damage output scales very well with SP usage."""

    sorting_key = (rotation.num_turns,
                   -rotation.turns.count("EB3"), -rotation.turns.count("EB2"),
                   -rotation.turns.count("EB1"), -rotation.turns.count("BASIC"))

    return sorting_key
