"""This module is responsible for applying all bonuses to the character's stats,
and run all the necessary calculation.

These bonuses include:
    - Character bonuses (Eidolons, Talents, Abilities)
    - Equipment (Light Cone, Rope, Ornaments)
    - other bonuses, such as ones provided by teammates.
    
These calculations include:
    - Basic attack only rotation, and the required ER for the next breakpoint.
    - Skill only rotation, and the needed ER for the next breakpoint.
    - One-skill rotation, perfect for checking if your rotation aligns with buff/debuff durations
    (e.g., Tingyun, SW, etc.).
    - Shortest, most skill-positive rotation, i.e.,
    it prioritizes rotations with the lowest skill point cost,
    if multiple rotations are eligible."""

from typing import Optional
from calculations_utils import (CalculationResults, Counters, print_results,
                                print_results_blade, find_basic_only_rotation,
                                find_best_rotation, find_one_skill_rotation,
                                find_skill_only_rotation, follow_up_attack_check,
                                get_er_threshold, quid_pro_quo_check)
from gui_utils import UserInput
from characters import CharStats
from eidolons import apply_eidolons
from talents import apply_talents
from abilities import apply_abilities
from light_cones import apply_light_cone
from relics import apply_ornament, apply_rope


def run_calculations(stats: CharStats, user_input: UserInput) -> None:
    """Applies all bonuses, runs all necessary calculations,
    and prints their results to the console."""

    _apply_bonuses(stats, user_input)
    results = _dfs_rotation_calculation(stats, user_input)

    if not results:
        return

    if user_input.char_name == "Blade":
        print_results_blade(stats.energy_recharge, user_input, results)

    else:
        print_results(stats.energy_recharge, user_input, results)


def _apply_bonuses(stats: CharStats, user_input: UserInput) -> None:
    """Applies all user-selected bonuses."""

    if user_input.char_name == "Blade":
        stats.skill = stats.basic + 10

    elif user_input.char_name == "Clara":
        stats.get_hit += 5

    elif user_input.char_name == "Trailblazer (Preservation)":
        stats.ult_act += 10

    if user_input.assume_tingyun_ult:
        stats.init_energy += 50

    if user_input.assume_tingyun_ult and user_input.assume_tingyun_e6:
        stats.init_energy += 10

    if user_input.assume_ult:
        stats.init_energy += stats.ult_act * stats.energy_recharge

    if user_input.num_ult_kills > 0:
        stats.init_energy += (user_input.num_ult_kills *
                              stats.ult_kill * stats.energy_recharge)
    
    stats.basic *= stats.energy_recharge
    stats.skill *= stats.energy_recharge

    apply_eidolons(stats, user_input.char_name, user_input.eidolons)
    apply_talents(stats, user_input.char_name, user_input.talent_level)
    apply_abilities(stats, user_input.ability)

    apply_light_cone(stats, user_input.light_cone, user_input.superimposition)
    apply_rope(stats, user_input.rope)
    apply_ornament(stats, user_input.ornament)



def _dfs_rotation_calculation(stats: CharStats,
                              user_input: UserInput) -> Optional[CalculationResults]:
    """Depth-first search algorithm that determines
    the shortest and most skill-point positive rotation.
    Positive rotations are defined as those that use more basic attacks than skills,
    as the former generate skill points, and the latter consume them."""

    quid_pro_quo_bonus = quid_pro_quo_check(
        user_input.light_cone, user_input.superimposition)
    follow_up_energy = follow_up_attack_check(user_input.char_name)

    relic_energy = user_input.relic.recharge_value if user_input.relic else 0
    counters = Counters()

    needed_energy = stats.ult_cost - stats.init_energy
    current = stats.init_energy

    stack: list = [(0, [])]
    all_turns: list[list[str]] = []

    while stack:
        current, turns = stack.pop()

        if round(current) >= needed_energy:
            all_turns.append(turns)
            continue

        if quid_pro_quo_bonus and current <= stats.ult_cost / 2:
            current += quid_pro_quo_bonus

        turn_energy = _calculate_turn_energy(
            stats, user_input, relic_energy, follow_up_energy, counters)

        stack.append((current + stats.basic + turn_energy, turns + ["BASIC"]))
        stack.append((current + stats.skill + turn_energy, turns + ["SKILL"]))

    basic_rot = find_basic_only_rotation(all_turns)
    basic_er_threshold = get_er_threshold(basic_rot, stats.energy_recharge)
    one_skill_rotation = find_one_skill_rotation(all_turns)

    skill_rot = find_skill_only_rotation(all_turns)
    skill_er_threshold = get_er_threshold(skill_rot, stats.energy_recharge)
    best_rotation = find_best_rotation(all_turns)

    return CalculationResults(basic_rot, basic_er_threshold, skill_rot,
                              skill_er_threshold, one_skill_rotation, best_rotation)


def _calculate_turn_energy(stats: CharStats, user_input: UserInput, relic_energy: float,
                           follow_up_energy: float, counters: Counters) -> float:
    """Calculates the energy generated during each turn based on user inputs."""

    turn_energy: float = 0

    if user_input.num_follow_ups == "every turn":
        turn_energy += follow_up_energy
    elif counters.follow_up_counter < user_input.num_follow_ups:
        turn_energy += follow_up_energy
        counters.follow_up_counter += 1

    if user_input.num_kills == "every turn":
        turn_energy += stats.kill
    elif counters.kill_counter < user_input.num_kills:
        turn_energy += user_input.num_kills * stats.kill
        counters.kill_counter += 1

    if user_input.num_hits_taken == "every turn":
        turn_energy += stats.get_hit
    elif counters.hit_counter < user_input.num_hits_taken:
        turn_energy += user_input.num_hits_taken * stats.get_hit
        counters.hit_counter += 1

    if user_input.num_relic_trigger == "every turn":
        turn_energy += relic_energy
    elif counters.relic_trigger_counter < user_input.num_relic_trigger:
        turn_energy += user_input.num_relic_trigger * relic_energy
        counters.relic_trigger_counter += 1

    return turn_energy * stats.energy_recharge
