"""This module contains a specific algorithm for Jingliu."""

from character_utils.characters import CharStats
from gui_scripts.user_input import UserInput
from equipment_utils.support_light_cones import apply_support_lcs
from calculation_scripts.rotation import RotationList
from calculation_scripts.calculations_utils import calculate_turn_energy


def dfs_algorithm_jingliu(stats: CharStats, user_input: UserInput) -> RotationList:
    """Jingliu possesses the ability to enter a buffed state
    when she gains enough Syzygy stacks.
    These stacks are gained by using Ultimates, Skills, technique.
    While she is in her buffed state,
    seh can only use Enhanced Skills at no Skill Point Cost."""

    syzygy_stacks = _prep_init_stats(stats, user_input)
    buffed_state = False
    all_rotations = RotationList()
    stack = [(stats.init_energy, [], 0, syzygy_stacks)]

    while stack:
        curr_energy, turns, skill_points_generated, syzygy_stacks = stack.pop()

        if curr_energy >= stats.ult_cost:
            all_rotations.add_rotation(curr_energy, turns,
                                       skill_points_generated)
            continue

        curr_energy = apply_support_lcs(stats, user_input, curr_energy)
        curr_energy += calculate_turn_energy(user_input)

        buffed_state, syzygy_stacks = buffed_state_check(buffed_state,
                                                         user_input.eidolon_level,
                                                         syzygy_stacks)

        # Jingliu enters buffed state where she can only use Enhanced Skills
        if buffed_state:
            stack.append((curr_energy + stats.e_skill,
                          turns + ["E. SKILL"],
                          skill_points_generated,
                          syzygy_stacks - 1))

        if not buffed_state:
            # Jingliu uses Basic Attack
            stack.append((curr_energy + stats.basic,
                          turns + ["BASIC"],
                          skill_points_generated + 1,
                          syzygy_stacks))

            # Jingliu uses Skill
            stack.append((curr_energy + stats.skill,
                          turns + ["SKILL"],
                          skill_points_generated - 1,
                          syzygy_stacks + 1))

    return all_rotations


def _prep_init_stats(stats: CharStats, user_input: UserInput) -> int:
    initial_syzygy_stacks = 1 * user_input.assume_ult
    if user_input.technique:
        stats.init_energy += 15 * stats.energy_recharge
        initial_syzygy_stacks += 1 * user_input.technique

    return initial_syzygy_stacks


def buffed_state_check(buffed_state: bool, eidolon_level: int, syzygy_stacks: int) -> tuple[bool, int]:
    """Checks whether Jingliu has enough Syzygy stacks to enter her buffed state.
    Returns whether or not she's enter the state, as well as the current number of stacks,
    this number can be increased if she has her Eidolon 6."""

    if syzygy_stacks == 2:
        buffed_state = True
        syzygy_stacks += 1 * eidolon_level == 6

    elif syzygy_stacks == 0:
        buffed_state = False

    return buffed_state, syzygy_stacks
