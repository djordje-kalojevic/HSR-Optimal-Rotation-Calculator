from typing import Callable
from character_utils.characters import CharStats
from equipment_utils.support_light_cones import apply_support_lcs
from gui_scripts.user_input import UserInput
from ..character_algorithms.default_algorithm import print_results_default
from calculation_scripts.rotation import RotationList
from calculation_scripts.calculations_utils import calculate_turn_energy


def dfs_algorithm_argenti(stats: CharStats, user_input: UserInput) -> RotationList:

    all_rotations = RotationList()
    stack = [(stats.init_energy, [], 0)]

    while stack:
        curr_energy, turns, skill_points_generated = stack.pop()

        if curr_energy >= stats.ult_cost:
            all_rotations.add_rotation(curr_energy, turns,
                                       skill_points_generated)
            continue

        curr_energy = apply_support_lcs(stats, user_input, curr_energy)
        curr_energy += calculate_turn_energy(user_input)

        # Argenti uses Basic Attack
        stack.append((curr_energy + stats.basic,
                     turns + ["BASIC"],
                     skill_points_generated + 1))

        # Argenti uses Skill
        stack.append((curr_energy + stats.skill,
                     turns + ["SKILL"],
                     skill_points_generated - 1))

    return all_rotations


def print_results_argenti(stats: CharStats, user_input: UserInput,
                          unique_rotations: RotationList,
                          algorithm: Callable[[CharStats, UserInput], RotationList]) -> None:
    """Argenti can use two types of his Ultimate, costing 90 and 180 energy respectively."""

    print_results_default(stats, user_input, unique_rotations, algorithm)

    stats.retrieve_cache("before-er-application", delete_cache=True)
    stats.ult_cost = 90
    stats.cache("before-er-application")

    unique_rotations = dfs_algorithm_argenti(stats, user_input)
    print_results_default(stats, user_input, unique_rotations, algorithm)
