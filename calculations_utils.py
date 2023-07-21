from dataclasses import dataclass
from typing import Optional

from termcolor import colored
from follow_ups import FOLLOW_UP_ATTACKS
from gui_utils import UserInput
from light_cones import LIGHT_CONES


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


@dataclass(slots=True)
class Counters:
    """Dataclass that represents various counters.

    Attributes:
        - Kill counter.
        - Counter of how many times character was hit.
        - Counter of how many times the relic effect was triggered.
        - Follow-up attack counter"""

    kill_counter: int = 0
    hit_counter: int = 0
    relic_trigger_counter: int = 0
    follow_up_counter: int = 0


def get_er_threshold(rotation: int, energy_recharge: float) -> float:
    """Calculates the energy threshold required for a given rotation."""

    shorter_rot = rotation - 1 if rotation > 1 else 1
    return round((1 / shorter_rot - energy_recharge + 1) * 100, 3)


def follow_up_attack_check(char_name: str) -> float:
    """Checks whether this character character has follow-up attacks,
    if so returns the bonus energy they generate."""

    follow_up_attack = FOLLOW_UP_ATTACKS.get(char_name)
    return follow_up_attack.energy_value if follow_up_attack else 0


def quid_pro_quo_check(light_cone: str, superimposition: int) -> float:
    """Checks whether the QPQ Light Cone is equipped,
    if so returns the it's bonus value, else it returns 0."""

    if not light_cone == "Quid Pro Quo":
        return 0

    return LIGHT_CONES["Quid Pro Quo"].superimpositions[superimposition]


def find_basic_only_rotation(lists_turns: list[list[str]]) -> int:
    """Finds shortest rotation that contains only basic attacks."""

    for rotation in lists_turns:
        if rotation.count("SKILL") > 0:
            continue
        return len(rotation)

    return 0


def find_skill_only_rotation(lists_turns: list[list[str]]) -> int:
    """Finds shortest rotation that contains only skills."""

    for rotation in lists_turns:
        if rotation.count("BASIC") > 0:
            continue
        return len(rotation)

    return 0


def find_one_skill_rotation(lists_turns: list[list[str]]) -> str:
    """Finds shortest rotation that contains only one skill."""

    for best_rotation in lists_turns:
        if best_rotation.count("SKILL") == 1:
            best_rotation = sorted(best_rotation, reverse=True)
            return _order_rotation_turns(best_rotation)

    return ""


def find_best_rotation(lists_turns: list[list[str]]) -> str:
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


def print_results(energy_recharge: float,
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

    if LIGHT_CONES.get(user_input.light_cone):
        char_info += f" and S{user_input.superimposition + 1} {user_input.light_cone}"

    print(colored(char_info, "green"))

    print(f"Basic only rotation: {results.basic_rot} x BASIC")
    print(f"ER needed for the next breakpoint: {results.basic_er_threshold}%")
    print(f"Skill only rotation: {results.skill_rot} x SKILL")
    print(f"ER needed for the next breakpoint: {results.skill_er_threshold}%")

    if results.one_skill_rotation:
        print(f"One skill rotation: {results.one_skill_rotation}")

    print(f"Most optimal rotation: {results.best_rotation}\n")


def print_results_blade(energy_recharge: float,
                        user_input: UserInput, results: CalculationResults) -> None:
    energy_recharge = round(energy_recharge * 100, 3)
    char_info = f"{user_input.char_name} with {energy_recharge}% ER"

    if LIGHT_CONES.get(user_input.light_cone):
        char_info += f" and S{user_input.superimposition + 1} {user_input.light_cone}"

    print(colored(char_info, "green"))

    print(f"Basic rotation: {results.basic_rot} x BASIC")
    print(f"ER needed for the next breakpoint: {results.basic_er_threshold}%")
    print(f"Enchanted Basic rotation: {results.skill_rot} x Enchanted Basics")
    print(f"ER needed for the next breakpoint: {results.skill_er_threshold}%")
