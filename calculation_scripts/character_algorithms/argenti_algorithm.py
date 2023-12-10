from characters import CharStats
from support_light_cones import apply_support_lcs
from gui_scripts.user_input import UserInput
from ..character_algorithms.default_algorithm import print_results_default
from calculation_scripts.rotation import RotationList
from calculation_scripts.calculations_utils import calculate_turn_energy


def dfs_algorithm_argenti(stats: CharStats, user_input: UserInput) -> RotationList:

    _prep_init_stats(stats, user_input)
    all_rotations = RotationList()
    stack = [(stats.init_energy, [], 0)]

    while stack:
        curr_energy, turns, skill_points_generated = stack.pop()

        if curr_energy >= stats.ult_cost:
            all_rotations.add_rotation(curr_energy, turns,
                                       skill_points_generated)
            continue

        curr_energy = apply_support_lcs(stats, user_input, curr_energy)
        turn_energy = calculate_turn_energy(stats, user_input)

        # Argenti uses Basic Attack
        stack.append((curr_energy + stats.basic + turn_energy,
                     turns + ["BASIC"], skill_points_generated + 1))

        # Argenti uses Skill
        stack.append((curr_energy + stats.skill + turn_energy,
                     turns + ["SKILL"], skill_points_generated - 1))

    return all_rotations


def _prep_init_stats(stats: CharStats, user_input: UserInput) -> None:
    user_input.cache("Argenti")

    enemy_hit_bonus = 3 * stats.energy_recharge
    stats.basic += enemy_hit_bonus
    stats.skill += enemy_hit_bonus * user_input.enemy_count

    if user_input.assume_ult:
        stats.init_energy += enemy_hit_bonus * user_input.enemy_count
    if user_input.technique:
        stats.init_energy += 15 * stats.energy_recharge


def print_results_argenti(stats: CharStats, user_input: UserInput, unique_rotations: RotationList):
    """Argenti can use two types of his Ultimate, costing 90 and 180 energy respectively."""

    print_results_default(stats, user_input, unique_rotations)
    user_input.retrieve_cache("Argenti")

    stats.ult_cost = 90
    unique_rotations = dfs_algorithm_argenti(stats, user_input)
    unique_rotations.process_rotation_data(user_input.char_name)
    print_results_default(stats, user_input, unique_rotations)
