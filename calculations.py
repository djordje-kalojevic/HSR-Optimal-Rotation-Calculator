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

from calculations_utils import (CalculationResults, determine_initial_energy, remove_permutations,
                                print_results, print_results_blade,
                                find_basic_only_rotation, find_best_rotation,
                                find_one_skill_rotation, find_skill_only_rotation,
                                follow_up_attack_check, get_er_breakpoint, quid_pro_quo_check)
from detailed_breakdown import print_detailed_breakdown
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
        print_results_blade(stats, user_input, results.best_rotation)

    else:
        print_results(stats.energy_recharge, user_input, results)

    if user_input.detailed_breakdown:
        print_detailed_breakdown(stats, user_input, results.best_rotation)


def _apply_bonuses(stats: CharStats, user_input: UserInput) -> None:
    """Applies all user-selected bonuses."""

    determine_initial_energy(stats, user_input)
    apply_eidolons(stats, user_input.char_name, user_input.eidolons)
    apply_talents(stats, user_input.char_name, user_input.talent_level)
    apply_abilities(stats, user_input.ability)

    apply_light_cone(stats, user_input.light_cone, user_input.superimposition)
    apply_rope(stats, user_input.rope)
    apply_ornament(stats, user_input.ornament)

    stats.follow_up = follow_up_attack_check(user_input.char_name)
    if user_input.char_name == "Clara":
        stats.get_hit += stats.follow_up

    stats.apply_energy_recharge()

    # not affected by energy recharge
    if user_input.assume_tingyun_ult:
        stats.init_energy += 50

    if user_input.assume_tingyun_ult and user_input.assume_tingyun_e6:
        stats.init_energy += 10


def _rotation_calculation(stats: CharStats,
                          user_input: UserInput) -> CalculationResults:
    all_turns = _apply_correct_algorithm(stats, user_input)
    unique_rotations = remove_permutations(all_turns)

    basic_rot = find_basic_only_rotation(unique_rotations)
    basic_er_threshold = get_er_breakpoint(basic_rot, stats.basic,
                                           stats.ult_cost, stats.init_energy)
    one_skill_rotation = find_one_skill_rotation(unique_rotations)

    skill_rot = find_skill_only_rotation(unique_rotations)
    skill_er_threshold = get_er_breakpoint(skill_rot, stats.skill,
                                           stats.ult_cost, stats.init_energy)
    best_rotation = find_best_rotation(unique_rotations)

    return CalculationResults(basic_rot, basic_er_threshold, skill_rot,
                              skill_er_threshold, one_skill_rotation, best_rotation)


def _apply_correct_algorithm(stats: CharStats, user_input: UserInput) -> list[list[str]]:
    if user_input.char_name == "Blade":
        all_turns = _dfs_algorithm_blade(stats, user_input)

    elif user_input.char_name == "Trailblazer (Preservation)":
        all_turns = _dfs_algorithm_fire_mc(stats, user_input)

    elif user_input.char_name == "Luka":
        all_turns = _dfs_algorithm_luka(stats, user_input)

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

    relic_energy = user_input.relic.recharge_value if user_input.relic else 0
    current = stats.init_energy

    all_turns: list[list[str]] = []
    stack: list = [(current, all_turns)]

    while stack:
        current, turns = stack.pop()

        if current >= stats.ult_cost:
            all_turns.append(turns)
            continue

        if quid_pro_quo_bonus and current <= stats.ult_cost / 2:
            current += quid_pro_quo_bonus

        turn_energy = _calculate_turn_energy(stats, user_input, relic_energy)

        stack.append((current + stats.basic + turn_energy, turns + ["BASIC"]))
        stack.append((current + stats.skill + turn_energy, turns + ["SKILL"]))

    return all_turns


def _calculate_turn_energy(stats: CharStats, user_input: UserInput, relic_energy: float) -> float:
    """Calculates the energy generated during each turn based on user inputs.
    This includes follow-up attacks, kills, hits taken, and relic triggers."""

    turn_energy: float = 0

    if user_input.num_follow_ups == "every turn":
        turn_energy += stats.follow_up

    if user_input.num_kills == "every turn":
        turn_energy += stats.kill

    if user_input.num_hits_taken == "every turn" and user_input.char_name != "Blade":
        turn_energy += stats.get_hit

    if user_input.num_relic_trigger == "every turn":
        turn_energy += relic_energy

    return turn_energy


def _dfs_algorithm_fire_mc(stats: CharStats, user_input: UserInput) -> list[list[str]]:
    """Trailblazer (PReservation), or Fire MC for short,
    possesses the ability to use enhanced basic attacks
    which generate more energy (30 base, same as skill).
    They cost 4 stacks, which are gained by attacking, using skills, or being attacks.
    One enhanced attack is guaranteed after using ultimate."""

    stats.e_basic = stats.basic + 10 * stats.energy_recharge

    quid_pro_quo_bonus = quid_pro_quo_check(
        user_input.light_cone, user_input.superimposition)

    relic_energy = user_input.relic.recharge_value if user_input.relic else 0
    current = stats.init_energy

    e_basic_cost = 4
    mc_stacks = e_basic_cost if user_input.assume_ult else 0
    if user_input.num_hits_taken != "every turn":
        mc_stacks += user_input.num_hits_taken

    all_turns: list[list[str]] = []
    stack: list = [(current, all_turns)]

    while stack:
        current, turns = stack.pop()

        if current >= stats.ult_cost:
            all_turns.append(turns)
            continue

        if quid_pro_quo_bonus and current <= stats.ult_cost / 2:
            current += quid_pro_quo_bonus

        turn_energy = _calculate_turn_energy(stats, user_input, relic_energy)

        if user_input.num_hits_taken == "every turn":
            mc_stacks += 1

        # Fire MC uses Enhanced Basic
        if mc_stacks >= e_basic_cost:
            stack.append((current + stats.e_basic + turn_energy,
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
    quid_pro_quo_bonus = quid_pro_quo_check(user_input.light_cone,
                                            user_input.superimposition)
    relic_energy = user_input.relic.recharge_value if user_input.relic else 0
    current = stats.init_energy

    follow_up_cost = 5
    if user_input.eidolons == 6:
        follow_up_cost = follow_up_cost - 1

    e_basic_charges = 3
    blade_stacks = 1 * user_input.assume_ult + 1 * user_input.technique
    if user_input.num_hits_taken != "every turn":
        blade_stacks += user_input.num_hits_taken

    all_turns: list[list[str]] = []
    stack: list = [(current, all_turns)]

    while stack:
        current, turns = stack.pop()

        if current >= stats.ult_cost:
            all_turns.append(turns)
            continue

        if quid_pro_quo_bonus and current <= stats.ult_cost / 2:
            current += quid_pro_quo_bonus

        turn_energy = _calculate_turn_energy(stats, user_input, relic_energy)

        if user_input.num_hits_taken == "every turn":
            blade_stacks += 1

        # Blade uses skill
        if e_basic_charges == 0:
            stack.append((current + turn_energy, turns))
            blade_stacks += 1
            e_basic_charges = 3

        # Blade has enough stacks for a follow-up attack
        if blade_stacks >= follow_up_cost:
            stack.append((current + turn_energy + stats.follow_up, turns))
            blade_stacks -= follow_up_cost

        # Blade uses Enhanced Basic
        if e_basic_charges > 0:
            stack.append((current + turn_energy + stats.e_basic,
                          turns + ["E. BASIC"]))
            blade_stacks += 1
            e_basic_charges -= 1

    return all_turns


def _dfs_algorithm_luka(stats: CharStats, user_input: UserInput):
    """Luka possesses the ability to use enhanced basic attacks but they generate
    the same amount of energy as a regular basic attack.
    These attacks cost two stacks which are generated by basic attacks, skills, and ultimates.
    These stacks are gained by attacking, using skills, using ultimates, or being attacks.
    Gaining these stacks also provide provide a small amount of energy."""

    stats.e_basic = stats.basic
    quid_pro_quo_bonus = quid_pro_quo_check(user_input.light_cone,
                                            user_input.superimposition)
    relic_energy = user_input.relic.recharge_value if user_input.relic else 0
    current = stats.init_energy
    stack_energy_bonus = 3 * stats.energy_recharge

    # one stack at the start of the battle, + 2 on ult use, +1 on technique use
    luka_stacks = 1 + 2 * user_input.assume_ult + 1 * user_input.technique
    current += 2 * stack_energy_bonus * user_input.assume_ult
    e_basic_cost = 2

    enemy_phys_weak = False
    if user_input.matching_enemy_weakness and user_input.eidolons >= 2:
        enemy_phys_weak = True

    all_turns: list[list[str]] = []
    stack: list = [(current, luka_stacks, all_turns)]

    while stack:
        current, luka_stacks, turns = stack.pop()

        if current >= stats.ult_cost:
            all_turns.append(turns)
            continue

        if quid_pro_quo_bonus and current <= stats.ult_cost / 2:
            current += quid_pro_quo_bonus

        turn_energy = _calculate_turn_energy(stats, user_input, relic_energy)

        # Luka uses Enhanced Basic
        if luka_stacks >= e_basic_cost:
            stack.append((current + stats.e_basic + turn_energy,
                          luka_stacks - e_basic_cost, turns + ["E. BASIC"]))

        # Luka uses Basic, generating one stack and 3 energy
        stack.append((current + stats.basic + turn_energy + stack_energy_bonus,
                     luka_stacks + 1, turns + ["BASIC"]))

        # Luka uses Skill, generating one stack and 3 energy,
        # and additionally one stack and 3 energy if enemy has physical weakness
        stack.append(((current + stats.skill + turn_energy
                       + stack_energy_bonus + stack_energy_bonus * enemy_phys_weak),
                     luka_stacks + 1 + 1 * enemy_phys_weak, turns + ["SKILL"]))

    return all_turns
