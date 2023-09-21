from calculation_scripts.calculations_utils import Rotation, calculate_turn_energy
from characters import CharStats
from gui_scripts.gui_utils import UserInput
from support_light_cones import apply_support_lcs


def dfs_algorithm_fx(stats: CharStats, user_input: UserInput):
    """Fu Xuan's skill creates a matrix field for 3 turns.
    Using another skill during this time will generate additional energy."""

    stats.e_skill = stats.skill + 20 * stats.energy_recharge

    curr_energy = stats.init_energy
    matrix_duration = 2 if user_input.technique else 0
    skill_points_used = 0
    all_rotations: list[Rotation] = []
    stack: list = [(curr_energy, all_rotations,
                    skill_points_used, matrix_duration)]

    while stack:
        curr_energy, turns, skill_points_used, matrix_duration = stack.pop()

        if curr_energy >= stats.ult_cost:
            rotation = Rotation(curr_energy, turns, skill_points_used)
            all_rotations.append(rotation)
            continue

        curr_energy = apply_support_lcs(stats, user_input, curr_energy)
        turn_energy = calculate_turn_energy(stats, user_input)

        # Fu Xuan uses Skill
        if matrix_duration == 0:
            stack.append((curr_energy + stats.skill + turn_energy,
                          turns + ["SKILL"], skill_points_used + 1, 3))

        # Fu Xuan uses Enhanced Skill
        elif matrix_duration > 0:
            stack.append((curr_energy + stats.e_skill + turn_energy,
                          turns + ["E. SKILL"], skill_points_used + 1, 3))

        # Fu Xuan uses Basic attack
        stack.append((curr_energy + stats.basic + turn_energy,
                      turns + ["BASIC"], skill_points_used - 1,
                      matrix_duration - 1))

    return all_rotations
