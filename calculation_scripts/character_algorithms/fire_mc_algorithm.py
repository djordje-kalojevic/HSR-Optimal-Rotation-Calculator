"""This module contains a specific algorithm for Trailblazer (Preservation), i.e., Fire MC."""

from character_utils.characters import CharStats
from gui_scripts.user_input import UserInput
from equipment_utils.support_light_cones import apply_support_lcs
from calculation_scripts.rotation import RotationList
from calculation_scripts.calculations_utils import calculate_turn_energy


def dfs_algorithm_fire_mc(stats: CharStats, user_input: UserInput) -> RotationList:
    """Trailblazer (Preservation), or Fire MC for short,
    possesses the ability to use enhanced basic attacks
    which generate more energy (30 base, same as skill).
    They cost 4 stacks, which are gained by attacking, using skills, or being attacks.
    One enhanced attack is guaranteed after using ultimate."""

    e_basic_cost, fire_mc_stacks = _prep_init_stats(user_input)
    all_rotations = RotationList()
    stack = [(stats.init_energy, [], 0, fire_mc_stacks)]

    while stack:
        curr_energy, turns, skill_points_generated, fire_mc_stacks = stack.pop()

        if curr_energy >= stats.ult_cost:
            all_rotations.add_rotation(curr_energy, turns,
                                       skill_points_generated)
            continue

        fire_mc_stacks = _gain_stacks(user_input, fire_mc_stacks)
        curr_energy = apply_support_lcs(stats, user_input, curr_energy)
        curr_energy += calculate_turn_energy(user_input)

        # Fire MC uses Enhanced Basic
        if fire_mc_stacks >= e_basic_cost:
            stack.append((curr_energy + stats.e_basic,
                          turns + ["E. BASIC"],
                          skill_points_generated + 1,
                          fire_mc_stacks - e_basic_cost))

        stack.append((curr_energy + stats.basic,
                      turns + ["BASIC"],
                      skill_points_generated + 1,
                      fire_mc_stacks + 1))

        stack.append((curr_energy + stats.skill,
                      turns + ["SKILL"],
                      skill_points_generated - 1,
                      fire_mc_stacks + 1))

    return all_rotations


def _prep_init_stats(user_input: UserInput) -> tuple[int, int]:
    e_basic_cost = 4
    fire_mc_stacks = e_basic_cost if user_input.assume_ult else 0

    return e_basic_cost, fire_mc_stacks


def _gain_stacks(user_input: UserInput, stacks: int) -> int:
    """Gains stacks with every hit taken."""

    if user_input.hits_taken.repeat_every_turn:
        stacks += user_input.hits_taken.num_triggers

    elif user_input.hits_taken.num_triggers > 0:
        stacks += 1

    return stacks
