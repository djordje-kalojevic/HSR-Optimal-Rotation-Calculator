"""This module contains a specific algorithm for Dan Heng Imbibitor Lunae (DHIL)."""

from calculation_scripts.calculations_utils import Rotation, calculate_turn_energy, get_char_info
from characters import CharStats
from gui_scripts.gui_utils import UserInput
from support_light_cones import apply_support_lcs


def dfs_algorithm_dhil(stats: CharStats, user_input: UserInput):
    """Dan Heng Imbibitor Lunae, or DHIL for short,
    possesses the ability to use 3 levels of enhanced basic attacks
    which generate more energy (30, 35, 40 respectively).
    Their costs are 1, 2, and 3 skill points respectively."""

    stats.e_basic = stats.basic + 10 * stats.energy_recharge
    stats.e_basic_2 = stats.basic + 15 * stats.energy_recharge
    stats.e_basic_3 = stats.basic + 20 * stats.energy_recharge
    curr_energy = stats.init_energy

    skill_points_generated = 0 + 2 * user_input.assume_ult + 1 * user_input.technique
    if user_input.assume_ult and user_input.eidolons >= 2:
        skill_points_generated += 1

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

        stack.append((curr_energy + stats.e_basic + turn_energy,
                      turns + ["EB1"], skill_points_generated - 1))

        stack.append((curr_energy + stats.e_basic_2 + turn_energy,
                      turns + ["EB2"], skill_points_generated - 2))

        stack.append((curr_energy + stats.e_basic_3 + turn_energy,
                      turns + ["EB3"], skill_points_generated - 3))

    return all_rotations


def print_results_dhil(energy_recharge: float, user_input: UserInput,
                       all_rotations: list[Rotation]) -> Rotation:
    """Prints DHIL's various rotations. This includes his best, most effective rotation,
    as well as rotations with various skill point breakpoints.
    Such breakpoints include -0.5, -1.25, -1.5, -2, and -2.33 skill points per turn (SP/T)."""

    best_rotation = get_best_dhil_rotation(energy_recharge,
                                           user_input, all_rotations)
    print_dhil_rotation(all_rotations, sp_cost_per_turn=0)
    print_dhil_rotation(all_rotations, sp_cost_per_turn=-0.5)
    print_dhil_rotation(all_rotations, sp_cost_per_turn=-1.25)
    print_dhil_rotation(all_rotations, sp_cost_per_turn=-1.5)
    print_dhil_rotation(all_rotations, sp_cost_per_turn=-2)
    print_dhil_rotation(all_rotations, sp_cost_per_turn=-2.33)
    print("\n")

    return best_rotation


def get_best_dhil_rotation(energy_recharge: float, user_input: UserInput,
                           all_rotations: list[Rotation]) -> Rotation:
    """Finds, prints and returns the best DHIL rotation."""

    print(get_char_info(energy_recharge, user_input))

    best_rot = min(all_rotations, key=_get_best_rotation_sorting_key)
    print(f"Best rotation ({best_rot.energy_generated} energy, "
          f"{best_rot.sp_cost_per_turn} SP/T): {_order_turns_dhil(best_rot)}")

    return best_rot


def print_dhil_rotation(all_rotations: list[Rotation], sp_cost_per_turn: float) -> None:
    """Prints the best DHIL's rotation with the specified Skill Point cost per turn, or less."""

    rotation = min((r for r in all_rotations
                    if r.sp_cost_per_turn >= sp_cost_per_turn),
                   key=lambda r: _get_best_general_sorting_key(r))

    if sp_cost_per_turn == 0:
        print(f"Neutral rotation ({rotation.energy_generated} energy): "
              f"{_order_turns_dhil(rotation)}")
    else:
        print(f"{sp_cost_per_turn} SP/T rotation ({rotation.energy_generated} energy): "
              f"{_order_turns_dhil(rotation)}")


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


def _order_turns_dhil(rotation: Rotation) -> str:
    """Returns the list of turns in the following format:
    "A x EB3 > B x EB2 > C x EB1 > D x BASIC" where A, B, C
    and D are numbers of occurrences for level 3 Enhanced Basics,
    level 2 EBs, level 1 EBs, and Basic attacks respectively.
    These attacks are omitted if their occurrence equals 0."""

    turns = []

    if rotation.e_basic_3_count > 1:
        turns.append(f"{rotation.e_basic_3_count} x EB3")
    elif rotation.e_basic_3_count == 1:
        turns.append("EB3")

    if rotation.e_basic_2_count > 1:
        turns.append(f"{rotation.e_basic_2_count} x EB2")
    elif rotation.e_basic_2_count == 1:
        turns.append("EB2")

    if rotation.e_basic_count > 1:
        turns.append(f"{rotation.e_basic_count} x EB1")
    elif rotation.e_basic_count == 1:
        turns.append("EB1")

    if rotation.basic_count > 1:
        turns.append(f"{rotation.basic_count} x BASIC")
    elif rotation.basic_count == 1:
        turns.append("BASIC")

    return " > ".join(turns)
