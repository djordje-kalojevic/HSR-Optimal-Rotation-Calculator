"""This module is responsible for applying all bonuses to the character's stats,
and running all the necessary calculations.

These bonuses include:
    - Character bonuses (Eidolons, Talents, Traces)
    - Equipment (Light Cone, Rope, Ornaments)
    - other bonuses, such as ones provided by teammates.

These calculations include:
    - Neutral rotations where applicable, i.e.,
    rotations that cost an average of 0 skill points per turn
    - Basic attack only rotation, and the required ER for the next breakpoint.
    - Skill only rotation, and the needed ER for the next breakpoint.
    - One-skill rotation, perfect for checking if your rotation aligns with buff/debuff durations
    (e.g., Tingyun, SW, etc.).
    - Shortest, most skill-positive rotation, i.e.,
    it prioritizes rotations with the lowest skill point cost,
    if multiple rotations are eligible."""

from character_utils.follow_ups import follow_up_attack_check
from character_utils.characters import CharStats, HUOHUO_PERCENT_ENERGY_BONUSES
from character_utils.talents import apply_talents
from character_utils.eidolons import apply_eidolons
from character_utils.traces import apply_traces
from equipment_utils.light_cones import apply_light_cones
from equipment_utils.relics import apply_ornament, apply_rope
from gui_scripts.user_input import UserInput
from .character_algorithms.all_algorithms import apply_correct_algorithm, print_results
from .calculations_utils import (determine_ally_hit_energy, determine_initial_energy,
                                 determine_counter_energy_values, derive_special_action_values)


def run_calculations(stats: CharStats, user_input: UserInput) -> None:
    """Applies all bonuses, runs all necessary calculations,
    and prints their results to the console."""

    _apply_bonuses(stats, user_input)
    determine_counter_energy_values(stats, user_input)
    user_input.check_for_active_counters()
    unique_rotations = apply_correct_algorithm(stats, user_input)
    print_results(stats, user_input, unique_rotations, apply_correct_algorithm)


def _apply_bonuses(stats: CharStats, user_input: UserInput) -> None:
    """Applies all user-selected bonuses to the character stats,
    then applies the energy recharge (ER) to those updated stats,
    the adds bonuses that are not affected by ER, then returns those updated stats."""

    follow_up_attack_check(stats, user_input.char_name)
    apply_eidolons(stats, user_input)
    apply_traces(stats, user_input.trace)
    apply_talents(stats, user_input.talent)
    apply_light_cones(stats, user_input)
    apply_rope(stats, user_input.rope)
    apply_ornament(stats, user_input.ornament)

    determine_ally_hit_energy(stats, user_input)
    derive_special_action_values(stats, user_input)
    determine_initial_energy(stats, user_input)

    stats.apply_energy_recharge(stats.energy_recharge)

    # Raw energy bonuses (unaffected by Energy Recharge)
    if user_input.assume_tingyun_ult:
        stats.init_energy += 50

    elif user_input.assume_tingyun_ult and user_input.assume_tingyun_e6:
        stats.init_energy += 60

    if user_input.huohuo_ult_level > 0:
        bonus = HUOHUO_PERCENT_ENERGY_BONUSES[user_input.huohuo_ult_level - 1]
        stats.init_energy += bonus / 100 * stats.ult_cost
