"""This module contains a specific algorithm for Jingliu."""

from copy import deepcopy
from characters import CharStats
from gui_scripts.user_input import UserInput
from support_light_cones import apply_support_lcs
from calculation_scripts.rotation import RotationList
from calculation_scripts.calculations_utils import calculate_turn_energy


def dfs_algorithm_jingliu(stats: CharStats, user_input: UserInput) -> RotationList:
    """Jingliu possesses the ability to enter a buffed state when she gains enough Syzygy stacks.
    These stacks are gained by using Ultimates, Skills, technique.
    While she is in her buffed state, seh can only use Enhanced Skills at no Skill Point Cost."""

    syzygy_stacks = _prep_init_stats(stats, user_input)
    all_rotations = RotationList()
    stack = [(stats.init_energy, [], 0, syzygy_stacks)]

    while stack:
        curr_energy, turns, skill_points_generated, syzygy_stacks = stack.pop()

        if curr_energy >= stats.ult_cost:
            all_rotations.add_rotation(curr_energy, turns,
                                       skill_points_generated)
            continue

        curr_energy = apply_support_lcs(stats, user_input, curr_energy)
        turn_energy = calculate_turn_energy(stats, user_input)

        # Jingliu uses Basic Attack
        stack.append((curr_energy + stats.basic + turn_energy,
                     turns + ["BASIC"], skill_points_generated + 1,
                     syzygy_stacks))

        # Jingliu uses Skill
        if syzygy_stacks < 2:
            stack.append((curr_energy + stats.skill + turn_energy,
                          turns + ["SKILL"], skill_points_generated - 1,
                          syzygy_stacks + 1))

        # Jingliu enters buffed state where she can only use Enhanced Skills
        elif syzygy_stacks == 2:
            if user_input.eidolon_level == 6:
                syzygy_stacks += 1

            temp_user_input = deepcopy(user_input)

            while syzygy_stacks > 0:
                curr_energy = apply_support_lcs(stats,
                                                temp_user_input, curr_energy)
                turn_energy = calculate_turn_energy(stats, temp_user_input)

                curr_energy += stats.e_skill + turn_energy
                turns += ["E. SKILL"]
                syzygy_stacks -= 1

                stack.append((curr_energy, turns,
                              skill_points_generated, syzygy_stacks))

    return all_rotations


def _prep_init_stats(stats: CharStats, user_input: UserInput) -> int:
    stats.e_skill = stats.skill
    stats.skill -= 10 * stats.energy_recharge

    syzygy_stacks = 1 * user_input.assume_ult
    if user_input.technique:
        stats.init_energy += 15 * stats.energy_recharge
        syzygy_stacks += 1 * user_input.technique

    return syzygy_stacks
