"""This module contains a specific algorithm for Trailblazer (Preservation), i.e., Fire MC."""

from calculation_scripts.calculations_utils import Rotation, calculate_turn_energy
from characters import CharStats
from gui_scripts.gui_utils import UserInput
from support_light_cones import apply_support_lcs


def dfs_algorithm_fire_mc(stats: CharStats, user_input: UserInput) -> list[Rotation]:
    """Trailblazer (Preservation), or Fire MC for short,
    possesses the ability to use enhanced basic attacks
    which generate more energy (30 base, same as skill).
    They cost 4 stacks, which are gained by attacking, using skills, or being attacks.
    One enhanced attack is guaranteed after using ultimate."""

    stats.e_basic = stats.basic + 10 * stats.energy_recharge
    curr_energy = stats.init_energy

    e_basic_cost = 4
    fire_mc_stacks = e_basic_cost if user_input.assume_ult else 0

    skill_points_generated = 0
    all_rotations: list[Rotation] = []
    stack: list = [(curr_energy, all_rotations,
                    skill_points_generated, fire_mc_stacks)]

    while stack:
        curr_energy, turns, skill_points_generated, fire_mc_stacks = stack.pop()

        if curr_energy >= stats.ult_cost:
            rotation = Rotation(curr_energy, turns, skill_points_generated)
            all_rotations.append(rotation)
            continue

        curr_energy = apply_support_lcs(stats, user_input, curr_energy)
        turn_energy = calculate_turn_energy(stats, user_input)

        if user_input.num_hits_taken == "every turn" or user_input.num_hits_taken > 0:
            fire_mc_stacks += 1

        # Fire MC uses Enhanced Basic
        if fire_mc_stacks >= e_basic_cost:
            stack.append((curr_energy + stats.e_basic + turn_energy,
                          turns + ["E. BASIC"], skill_points_generated + 1,
                          fire_mc_stacks - e_basic_cost))

        stack.append((curr_energy + stats.basic + turn_energy,
                     turns + ["BASIC"], skill_points_generated + 1, fire_mc_stacks + 1))

        stack.append((curr_energy + stats.skill + turn_energy,
                     turns + ["SKILL"], skill_points_generated - 1, fire_mc_stacks + 1))

    return all_rotations
