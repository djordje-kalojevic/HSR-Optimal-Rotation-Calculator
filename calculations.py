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

from dataclasses import dataclass
from typing import Optional
from termcolor import colored
from gui_utils import UserInput
from characters import CharStats
from eidolons import apply_eidolons
from talents import apply_talents
from abilities import apply_abilities
from light_cones import LIGHT_CONES, apply_light_cone
from relics import apply_ornament, apply_rope


def run_calculations(stats: CharStats, user_input: UserInput) -> None:
    """Applies all bonuses, runs all necessary calculations,
    and prints their results to the console."""

    _apply_bonuses(stats, user_input)

    results = _dfs_rotation_calculation(stats, user_input)

    if results:
        _print_results(stats.energy_recharge, user_input, results)


def _apply_bonuses(stats: CharStats, user_input: UserInput) -> None:
    """Applies all user-selected bonuses."""

    if user_input.char_name == "Clara":
        stats.get_hit += 5

    if user_input.char_name == "Trailblazer (Preservation)":
        stats.ult_act += 10

    if user_input.assume_tingyun_ult:
        stats.init_energy += 50

    if user_input.assume_tingyun_ult and user_input.assume_tingyun_e6:
        stats.init_energy += 10

    apply_eidolons(stats, user_input.char_name, user_input.eidolons)
    apply_talents(stats, user_input.char_name, user_input.talent_level)
    apply_abilities(stats, user_input.ability)

    apply_light_cone(stats, user_input.light_cone, user_input.superimposition)
    apply_rope(stats, user_input.rope)
    apply_ornament(stats, user_input.ornament)


@dataclass(slots=True)
class CalculationResults:
    """Dataclass that represents calculation results.

    Attributes:
        - Basic attack only rotation, and the required ER for the next breakpoint.
        - Skill only rotation, and the needed ER for the next breakpoint.
        - One-skill rotation
        - Shortest, most skill-positive rotation"""

    basic_rot: int
    basic_er_threshold: float
    skill_rot: int
    skill_er_threshold: float
    one_skill_rotation: Optional[str]
    best_rotation: str


def _dfs_rotation_calculation(stats: CharStats,
                              user_input: UserInput) -> Optional[CalculationResults]:
    """Depth-first search algorithm that determines
    the shortest and most skill-point positive rotation.
    Positive rotations are defined as those that use more basic attacks than skills,
    as the former generate skill points, and the latter consume them."""

    stats.energy_recharge /= 100
    stats.basic *= stats.energy_recharge
    stats.skill *= stats.energy_recharge
    stats.kill *= stats.energy_recharge
    stats.get_hit *= stats.energy_recharge
    relic_energy = user_input.relic.recharge_value if user_input.relic else 0

    if user_input.light_cone == "Quid Pro Quo":
        quid_pro_quo = LIGHT_CONES.get("Quid Pro Quo")
        quid_pro_quo_er_bonus = quid_pro_quo.superimpositions[user_input.superimposition]

    if user_input.assume_ult:
        stats.init_energy += stats.ult_act * stats.energy_recharge

    if user_input.num_ult_kills > 0:
        stats.init_energy += user_input.num_ult_kills * \
            stats.ult_kill * stats.energy_recharge

    needed_energy = stats.ult_cost - stats.init_energy

    stack: list = [(0, [], 0, 0)]
    all_turns: list[list[str]] = []
    current = stats.init_energy

    while stack:
        current, turns, basic_count, skill_count = stack.pop()

        if round(current) >= needed_energy:
            all_turns.append(turns)
            continue

        if quid_pro_quo and current <= stats.ult_cost / 2:
            current += quid_pro_quo_er_bonus

        turn_energy: float = 0

        if user_input.num_kills == "every turn":
            turn_energy += stats.kill
        else:
            current += user_input.num_kills * stats.kill

        if user_input.num_hits_taken == "every turn":
            turn_energy += stats.get_hit
        else:
            current += user_input.num_hits_taken * stats.get_hit

        if user_input.num_relic_trigger == "every turn":
            turn_energy += relic_energy
        else:
            current += user_input.num_relic_trigger * relic_energy

        stack.append((current + stats.basic + turn_energy, turns + ["BASIC"],
                     basic_count + 1, skill_count))

        stack.append((current + stats.skill + turn_energy, turns + ["SKILL"],
                      basic_count, skill_count + 1))

    basic_rot = _find_basic_only_rotation(all_turns)
    skill_rot = _find_skill_only_rotation(all_turns)

    # energy needed to decrease rotations by one
    shorter_rot = basic_rot - 1 if basic_rot > 1 else 1
    basic_er_threshold = round(
        (1 / shorter_rot - stats.energy_recharge + 1) * 100, 3)
    shorter_rot = skill_rot - 1 if skill_rot > 1 else 1
    skill_er_threshold = round(
        (1 / shorter_rot - stats.energy_recharge + 1) * 100, 3)

    one_skill_rotation = _find_one_skill_rotation(all_turns)
    best_rotation = _find_best_rotation(all_turns)

    return CalculationResults(basic_rot, basic_er_threshold, skill_rot,
                              skill_er_threshold, one_skill_rotation, best_rotation)


def _find_basic_only_rotation(lists_turns: list[list[str]]) -> int:
    """Finds shortest rotation that contains only basic attacks."""

    for rotation in lists_turns:
        if rotation.count("SKILL") > 0:
            continue
        return len(rotation)

    return 0


def _find_skill_only_rotation(lists_turns: list[list[str]]) -> int:
    """Finds shortest rotation that contains only skills."""

    for rotation in lists_turns:
        if rotation.count("BASIC") > 0:
            continue
        return len(rotation)

    return 0


def _find_one_skill_rotation(lists_turns: list[list[str]]) -> str:
    """Finds shortest rotation that contains only one skill."""

    for best_rotation in lists_turns:
        if best_rotation.count("SKILL") == 1:
            best_rotation = sorted(best_rotation, reverse=True)
            return _order_rotation_turns(best_rotation)

    return ""


def _find_best_rotation(lists_turns: list[list[str]]) -> str:
    """Finds the best rotation, defined as the rotation with fewest turns,
    as well as the fewest skills."""

    min_length = min(len(l) for l in lists_turns)
    shortest_lists = [l for l in lists_turns if len(l) == min_length]
    best_rotation = []

    if len(shortest_lists) == 1:
        return _order_rotation_turns(shortest_lists[0])

    min_skills = 0
    while min_skills < min_length:
        for short_list in shortest_lists:
            if short_list.count("SKILL") == min_skills:
                best_rotation = sorted(short_list, reverse=True)
                return _order_rotation_turns(best_rotation)
        min_skills += 1

    return ""


def _order_rotation_turns(rotation: list[str]) -> str:
    """Returns the list of turns in the following format:
    "A x SKILL > B x BASIC" where A and B are numbers of occurrences
    for skills and basic attacks respectively. These numbers are omitted if they equal 0."""

    skill_count = rotation.count("SKILL")
    basic_count = rotation.count("BASIC")

    if skill_count == 0:
        return f"{basic_count} x BASIC" if basic_count > 1 else "BASIC"

    if basic_count == 0:
        return f"{skill_count} x SKILL" if skill_count > 1 else "SKILL"

    if skill_count > 1 and basic_count > 1:
        return f"{skill_count} x SKILL > {basic_count} x BASIC"

    if skill_count > 1:
        return f"{skill_count} x SKILL > BASIC"

    if basic_count > 1:
        return f"SKILL > {basic_count} x BASIC"

    return "SKILL > BASIC"


def _print_results(energy_recharge: float,
                   user_input: UserInput, results: CalculationResults) -> None:
    """Prints to the console the following:
        - character info: their name, energy recharge,
        Light Cone that's equipped and its superimposition
        - basic only rotation,
        and additional energy recharge needed to shorten th rotation by 1 turn
        - skill only rotation,
        and additional energy recharge needed to shorten this rotation by 1 turn
        - one skill rotation,
        useful for buffers/debuffers to see if rotation coincides with buff/debuff duration
        - Shortest, most skill-positive rotation, i.e.,
        it prioritizes rotations with the lowest skill point cost
        if multiple rotations are eligible."""

    energy_recharge = round(energy_recharge * 100, 3)
    char_info = f"{user_input.char_name} with {energy_recharge}% ER"

    if user_input.light_cone != "--Select Light Cone--":
        char_info += f" and S{user_input.superimposition + 1} {user_input.light_cone}"

    print(colored(char_info, "green"))

    print(f"Basic only rotation: {results.basic_rot} x BASIC")
    print(f"ER needed for the next breakpoint: {results.basic_er_threshold}%")
    print(f"Skill only rotation: {results.skill_rot} x SKILL")
    print(f"ER needed for the next breakpoint: {results.skill_er_threshold}%")

    if results.one_skill_rotation:
        print(f"One skill rotation: {results.one_skill_rotation}")

    print(f"Most optimal rotation: {results.best_rotation}\n")
