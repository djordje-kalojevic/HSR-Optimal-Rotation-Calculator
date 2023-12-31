"""This module contains a specific algorithm for Topaz."""

from character_utils.characters import CharStats
from gui_scripts.user_input import UserInput
from equipment_utils.support_light_cones import apply_support_lcs
from calculation_scripts.rotation import RotationList
from calculation_scripts.calculations_utils import calculate_turn_energy


def dfs_algorithm_topaz(stats: CharStats, user_input: UserInput) -> RotationList:
    numby_bonus_energy, numby_triggers = _prep_init_stats(stats, user_input)
    all_rotations = RotationList()
    stack = [(stats.init_energy, [], 0)]

    while stack:
        curr_energy, turns, skill_points_generated = stack.pop()

        if curr_energy >= stats.ult_cost:
            all_rotations.add_rotation(curr_energy, turns,
                                       skill_points_generated)
            continue

        if numby_triggers > 0:
            curr_energy += numby_bonus_energy
            numby_triggers -= 1

        curr_energy = apply_support_lcs(stats, user_input, curr_energy)
        curr_energy += calculate_turn_energy(user_input)

        # Topaz uses Basic Attack
        stack.append((curr_energy + stats.basic,
                     turns + ["BASIC"],
                     skill_points_generated + 1))

        # Topaz uses Skill
        stack.append((curr_energy + stats.skill,
                      turns + ["SKILL"],
                      skill_points_generated - 1))

    return all_rotations


def _prep_init_stats(stats: CharStats, user_input: UserInput) -> tuple[float, int]:
    if user_input.technique:
        stats.init_energy += 60 * stats.energy_recharge

    numby_bonus_energy = 10
    if user_input.eidolon_level >= 2:
        numby_bonus_energy += 5

    num_numby_triggers = 2 if user_input.assume_ult else 0

    return numby_bonus_energy * stats.energy_recharge, num_numby_triggers
