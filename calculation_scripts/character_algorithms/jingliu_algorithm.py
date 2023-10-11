from calculation_scripts.calculations_utils import Rotation, calculate_turn_energy
from characters import CharStats
from gui_scripts.gui_utils import UserInput
from support_light_cones import apply_support_lcs


def dfs_algorithm_jingliu(stats: CharStats, user_input: UserInput):
    """Jingliu possesses the ability to enter a buffed state when she gains enough Syzygy stacks.
    These stacks are gained by using Ultimates, Skills, technique.
    While she is in her buffed state, seh can only use Enhanced Skills at no Skill Point Cost."""

    stats.e_skill = stats.skill
    stats.skill -= 10 * stats.energy_recharge

    curr_energy = stats.init_energy
    syzygy_stacks = 0
    if user_input.technique:
        curr_energy += 15 * stats.energy_recharge
        syzygy_stacks += 1 * user_input.technique

    syzygy_stacks += 1 * user_input.assume_ult
    bonus_syzygy_stack = 1 if user_input.eidolons == 6 else 0
    skill_points_generated = 0
    all_rotations: list[Rotation] = []
    stack: list = [(curr_energy, all_rotations,
                    skill_points_generated, syzygy_stacks)]

    while stack:
        curr_energy, turns, skill_points_generated, syzygy_stacks = stack.pop()

        if curr_energy >= stats.ult_cost:
            rotation = Rotation(curr_energy, turns, skill_points_generated)
            all_rotations.append(rotation)
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
        if syzygy_stacks == 2:
            syzygy_stacks += bonus_syzygy_stack
            temp_user_input = user_input

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
