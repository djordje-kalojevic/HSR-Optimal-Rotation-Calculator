"""This module is responsible for applying all bonuses to the character's stats,
and run all the necessary calculations.

These bonuses include:
    - Character bonuses (Eidolons, Talents, Abilities)
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

from .calculations_utils import Rotation, determine_initial_energy
from .character_algorithms.default_algorithm import dfs_algorithm_default, print_results
from .character_algorithms.blade_algorithm import dfs_algorithm_blade, print_results_blade
from .character_algorithms.fu_xuan_algorithm import dfs_algorithm_fx
from .character_algorithms.fire_mc_algorithm import dfs_algorithm_fire_mc
from .character_algorithms.luka_algorithm import dfs_algorithm_luka
from .character_algorithms.DHIL_algorithm import dfs_algorithm_dhil, print_results_dhil
from .detailed_breakdown import print_detailed_breakdown
from follow_ups import follow_up_attack_check
from gui_scripts.gui_utils import UserInput
from characters import CharStats
from eidolons import apply_eidolons
from talents import apply_talents
from abilities import apply_abilities
from light_cones import apply_light_cones
from relics import apply_ornament, apply_rope


def run_calculations(stats: CharStats, user_input: UserInput) -> None:
    """Applies all bonuses, runs all necessary calculations,
    and prints their results to the console."""

    stats = _apply_bonuses(stats, user_input)
    all_rotations = _apply_correct_algorithm(stats, user_input)

    if user_input.char_name == "Blade":
        best_rotation = print_results_blade(stats, user_input, all_rotations)

    elif user_input.char_name == "Dan Heng IL":
        best_rotation = print_results_dhil(stats.energy_recharge,
                                           user_input, all_rotations)
    else:
        best_rotation = print_results(stats, user_input, all_rotations)

    if user_input.detailed_breakdown:
        print_detailed_breakdown(stats, user_input, best_rotation)


def _apply_bonuses(stats: CharStats, user_input: UserInput) -> CharStats:
    """Applies all user-selected bonuses to the character stats,
    then applies the energy recharge (ER) to those updated stats,
    the adds bonuses that are not affected by ER, then returns those updated stats."""

    apply_eidolons(stats, user_input.char_name, user_input.eidolons)
    apply_talents(stats, user_input.char_name, user_input.talent_level)
    apply_abilities(stats, user_input.ability)

    apply_light_cones(stats, user_input.light_cone,
                      user_input.support_light_cone)
    apply_rope(stats, user_input.rope)
    apply_ornament(stats, user_input.ornament)

    stats.follow_up = follow_up_attack_check(user_input.char_name)
    if user_input.char_name == "Clara":
        stats.get_hit += stats.follow_up

    stats.init_energy = determine_initial_energy(stats, user_input)
    stats.apply_energy_recharge(stats.energy_recharge)

    if user_input.assume_tingyun_ult:
        stats.init_energy += 50

    elif user_input.assume_tingyun_ult and user_input.assume_tingyun_e6:
        stats.init_energy += 60

    return stats


def _apply_correct_algorithm(stats: CharStats, user_input: UserInput) -> list[Rotation]:
    """Applies the correct Depth-First Search algorithm, that is,
    certain characters have their own customized algorithms, others use the default one."""

    if user_input.char_name == "Blade":
        all_rotations = dfs_algorithm_blade(stats, user_input)

    elif user_input.char_name == "Dan Heng IL":
        all_rotations = dfs_algorithm_dhil(stats, user_input)

    elif user_input.char_name == "Fu Xuan":
        all_rotations = dfs_algorithm_fx(stats, user_input)

    elif user_input.char_name == "Trailblazer (Preservation)":
        all_rotations = dfs_algorithm_fire_mc(stats, user_input)

    elif user_input.char_name == "Luka":
        all_rotations = dfs_algorithm_luka(stats, user_input)

    else:
        all_rotations = dfs_algorithm_default(stats, user_input)

    return all_rotations
