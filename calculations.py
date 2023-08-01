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
                                get_er_breakpoint, quid_pro_quo_check, remove_permutations)
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
    results = _rotation_calculation(stats, user_input)

    if not results:
        return

    if user_input.char_name == "Blade":
        print_results_blade(stats, user_input, results)

    else:
        print_results(stats.energy_recharge, user_input, results)


def _apply_bonuses(stats: CharStats, user_input: UserInput) -> None:
    """Applies all user-selected bonuses."""

    if user_input.char_name == "Clara":
        stats.get_hit += follow_up_attack_check(user_input.char_name)

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

    apply_eidolons(stats, user_input.char_name, user_input.eidolons)
    apply_talents(stats, user_input.char_name, user_input.talent_level)
    apply_abilities(stats, user_input.ability)

    apply_light_cone(stats, user_input.light_cone, user_input.superimposition)
    apply_rope(stats, user_input.rope)
    apply_ornament(stats, user_input.ornament)

    stats.basic = stats.basic * stats.energy_recharge
    stats.skill = stats.skill * stats.energy_recharge


def _rotation_calculation(stats: CharStats,
                          user_input: UserInput) -> Optional[CalculationResults]:
    all_turns = _apply_correct_algorithm(stats, user_input)
    unique_turns = remove_permutations(all_turns)

    basic_rot = find_basic_only_rotation(unique_turns)
    basic_er_threshold = get_er_breakpoint(
        basic_rot, stats.basic, stats.ult_cost)
    one_skill_rotation = find_one_skill_rotation(unique_turns)

    skill_rot = find_skill_only_rotation(unique_turns)
    skill_er_threshold = get_er_breakpoint(
        skill_rot, stats.skill, stats.ult_cost)
    best_rotation = find_best_rotation(unique_turns)

    return CalculationResults(basic_rot, basic_er_threshold, skill_rot,
                              skill_er_threshold, one_skill_rotation, best_rotation)


def _apply_correct_algorithm(stats: CharStats, user_input: UserInput) -> list[list[str]]:
    if user_input.char_name == "Blade":
        all_turns = _dfs_algorithm_blade(stats, user_input)

    elif user_input.char_name == "Trailblazer (Preservation)":
        all_turns = _dfs_algorithm_fire_mc(stats, user_input)

    else:
        all_turns = _dfs_algorithm_default(stats, user_input)
    return all_turns


def _dfs_algorithm_default(stats: CharStats, user_input: UserInput) -> list[list[str]]:
    """Default Depth-First Search algorithm that determines
    the shortest and most skill-point positive rotation.
    Positive rotations are defined as those that use more basic attacks than skills,
    as the former generate skill points, and the latter consume them."""

    quid_pro_quo_bonus = quid_pro_quo_check(
        user_input.light_cone, user_input.superimposition)
    follow_up_energy = follow_up_attack_check(user_input.char_name)

    relic_energy = user_input.relic.recharge_value if user_input.relic else 0
    current = stats.init_energy
    counters = Counters()

    stack: list = [(current, [])]
    all_turns: list[list[str]] = []

    while stack:
        current, turns = stack.pop()

        if current >= stats.ult_cost:
            all_turns.append(turns)
            continue

        if quid_pro_quo_bonus and current <= stats.ult_cost / 2:
            current += quid_pro_quo_bonus

        turn_energy = _calculate_turn_energy(
            stats, user_input, relic_energy, follow_up_energy, counters)

        stack.append((current + stats.basic + turn_energy, turns + ["BASIC"]))
        stack.append((current + stats.skill + turn_energy, turns + ["SKILL"]))

    return all_turns


def _calculate_turn_energy(stats: CharStats, user_input: UserInput, relic_energy: float,
                           follow_up_energy: float, counters: Counters) -> float:
    """Calculates the energy generated during each turn based on user inputs.
    This includes follow-up attacks, kills, hits taken, and relic triggers."""

    turn_energy: float = 0

    if user_input.num_follow_ups == "every turn":
        turn_energy += follow_up_energy
    elif counters.follow_up_counter < user_input.num_follow_ups:
        turn_energy += follow_up_energy
        counters.follow_up_counter = user_input.num_follow_ups

    if user_input.num_kills == "every turn":
        turn_energy += stats.kill
    elif counters.kill_counter < user_input.num_kills:
        turn_energy += user_input.num_kills * stats.kill
        counters.kill_counter = user_input.num_kills

    if user_input.num_hits_taken == "every turn":
        turn_energy += stats.get_hit
    elif counters.hit_counter < user_input.num_hits_taken:
        turn_energy += user_input.num_hits_taken * stats.get_hit
        counters.hit_counter = user_input.num_hits_taken

    if user_input.num_relic_trigger == "every turn":
        turn_energy += relic_energy
    elif counters.relic_trigger_counter < user_input.num_relic_trigger:
        turn_energy += user_input.num_relic_trigger * relic_energy
        counters.relic_trigger_counter = user_input.num_relic_trigger

    return turn_energy * stats.energy_recharge


def _dfs_algorithm_fire_mc(stats: CharStats, user_input: UserInput) -> list[list[str]]:
    """Trailblazer (PReservation), or Fire MC for short,
    possesses the ability to use enhanced basic attacks
    which generate more energy (30 base, same as skill).
    They cost 4 stacks, which are gained by attacking, using skills, or being attacks.
    One enhanced attack is guaranteed after using ultimate."""

    e_basic = stats.basic + 10 * stats.energy_recharge

    quid_pro_quo_bonus = quid_pro_quo_check(
        user_input.light_cone, user_input.superimposition)
    follow_up_energy = follow_up_attack_check(user_input.char_name)

    relic_energy = user_input.relic.recharge_value if user_input.relic else 0
    current = stats.init_energy
    counters = Counters()
    e_basic_cost = 4
    mc_stacks = e_basic_cost if user_input.assume_ult else 0

    stack: list = [(current, [])]
    all_turns: list[list[str]] = []

    while stack:
        current, turns = stack.pop()

        if current >= stats.ult_cost:
            all_turns.append(turns)
            continue

        if quid_pro_quo_bonus and current <= stats.ult_cost / 2:
            current += quid_pro_quo_bonus

        turn_energy = _calculate_turn_energy(
            stats, user_input, relic_energy, follow_up_energy, counters)

        if user_input.num_hits_taken == "every turn":
            mc_stacks += 1
        elif counters.hit_counter < user_input.num_hits_taken:
            counters.hit_counter = user_input.num_hits_taken
            mc_stacks += user_input.num_hits_taken

        if mc_stacks >= e_basic_cost:
            stack.append((current + e_basic + turn_energy,
                          turns + ["E. BASIC"]))
            mc_stacks -= e_basic_cost
            continue

        stack.append((current + stats.basic + turn_energy, turns + ["BASIC"]))
        stack.append((current + stats.skill + turn_energy, turns + ["SKILL"]))
        mc_stacks += 1

    return all_turns


def _dfs_algorithm_blade(stats: CharStats, user_input: UserInput):
    """Blade possesses the ability to use enhanced basic attacks that generate more energy.
    Skill grants 3 charges for these attacks, and does not end turn.
    Additionally he can perform follow-up attacks which cost 5 stacks (4 with Eidolon 6).
    These stacks are gained by attacking, using skills, using ultimates, or being attacks.
    Given his play-style, it is assumed it starts with a skill, thus one stack is assumed."""

    stats.e_basic = stats.basic + 10 * stats.energy_recharge

    quid_pro_quo_bonus = quid_pro_quo_check(
        user_input.light_cone, user_input.superimposition)
    follow_up_energy = follow_up_attack_check(user_input.char_name)
    follow_up_energy = follow_up_energy * stats.energy_recharge

    relic_energy = user_input.relic.recharge_value if user_input.relic else 0
    current = stats.init_energy
    counters = Counters()

    follow_up_cost = 5
    if user_input.eidolons == 6:
        follow_up_cost = follow_up_cost - 1

    blade_stacks = 1 + 1 * user_input.assume_ult + 1 * user_input.technique
    e_basic_charges = 3

    stack: list = [(current, [])]
    all_turns: list[list[str]] = []

    while stack:
        current, turns = stack.pop()

        if current >= stats.ult_cost:
            all_turns.append(turns)
            continue

        if quid_pro_quo_bonus and current <= stats.ult_cost / 2:
            current += quid_pro_quo_bonus

        turn_energy = _calculate_turn_energy_blade(
            stats, user_input, relic_energy, counters)

        if user_input.num_hits_taken == "every turn":
            blade_stacks += 1
        elif counters.hit_counter < user_input.num_hits_taken:
            counters.hit_counter = user_input.num_hits_taken
            blade_stacks += user_input.num_hits_taken

        if blade_stacks >= follow_up_cost:
            stack.append((current + turn_energy + follow_up_energy, turns))
            blade_stacks -= follow_up_cost

        if e_basic_charges == 0:
            stack.append((current + turn_energy, turns))
            blade_stacks += 1
            e_basic_charges = 3

        if e_basic_charges > 0:
            stack.append((current + turn_energy + stats.e_basic,
                          turns + ["E. BASIC"]))
            blade_stacks += 1
            e_basic_charges -= 1

    return all_turns


def _calculate_turn_energy_blade(stats: CharStats, user_input: UserInput,
                                 relic_energy: float, counters: Counters) -> float:
    """Calculates the energy generated during each turn based on user inputs."""

    turn_energy: float = 0

    if user_input.num_kills == "every turn":
        turn_energy += stats.kill
    elif counters.kill_counter < user_input.num_kills:
        turn_energy += user_input.num_kills * stats.kill
        counters.kill_counter = user_input.num_kills

    if user_input.num_hits_taken == "every turn":
        turn_energy += stats.get_hit
    elif counters.hit_counter < user_input.num_hits_taken:
        turn_energy += user_input.num_hits_taken * stats.get_hit
        counters.hit_counter = user_input.num_hits_taken

    if user_input.num_relic_trigger == "every turn":
        turn_energy += relic_energy
    elif counters.relic_trigger_counter < user_input.num_relic_trigger:
        turn_energy += user_input.num_relic_trigger * relic_energy
        counters.relic_trigger_counter = user_input.num_relic_trigger

    return turn_energy * stats.energy_recharge
