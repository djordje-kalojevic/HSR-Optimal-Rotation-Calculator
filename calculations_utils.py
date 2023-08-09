from dataclasses import dataclass
from typing import Optional
from termcolor import colored
from characters import CharStats
from detailed_breakdown import Rotation
from follow_ups import FOLLOW_UP_ATTACKS
from gui_utils import UserInput
from light_cones import LIGHT_CONES


@dataclass(slots=True, frozen=True)
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
    best_rotation: Rotation


def get_er_breakpoint(rotation: int, attack_value: float,
                      ult_cost: float, init_energy: float) -> float:
    """Calculates and returns the energy recharge breakpoint, i.e.,
    how much more ER is required to shorten such a rotation by one turn.
    Return 0% if the rotation in question is 1 turn long,
    as there could not possibly exist a shorter rotation."""

    if rotation - 1 == 0:
        return 0

    needed_attack_value = (ult_cost - init_energy) / (rotation - 1)
    return round((needed_attack_value / attack_value - 1) * 100, 3)


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


def find_basic_only_rotation(rotations: list[list[str]]) -> int:
    """Finds shortest rotation that contains only basic attacks."""

    for rotation in rotations:
        if rotation.count("SKILL") == 0:
            return len(rotation)

    return 0


def find_skill_only_rotation(rotations: list[list[str]]) -> int:
    """Finds shortest rotation that contains only skills."""

    for rotation in rotations:
        if rotation.count("BASIC") == 0:
            return len(rotation)

    return 0


def find_one_skill_rotation(rotations: list[list[str]]) -> str:
    """Finds shortest rotation that contains only one skill."""

    rotations = [lst for lst in rotations if lst.count("SKILL") == 1]
    if not rotations:
        return ""

    min_length = min(len(lst) for lst in rotations)
    shortest_rotations = [lst for lst in rotations if len(lst) == min_length]

    for rotation in shortest_rotations:
        return _order_rotation_turns(rotation).sequence

    return ""


def find_best_rotation(rotations: list[list[str]]) -> Rotation:
    """Finds the best rotation, defined as the rotation with fewest turns,
    as well as the fewest skills."""

    min_length = min(len(lst) for lst in rotations)
    shortest_rotations = [lst for lst in rotations if len(lst) == min_length]

    if len(shortest_rotations) == 1:
        return _order_rotation_turns(shortest_rotations[0])

    min_skills = 0
    while min_skills <= min_length:
        for rotation in shortest_rotations:
            if rotation.count("SKILL") == min_skills:
                return _order_rotation_turns(rotation)
        min_skills += 1

    return Rotation("")


def _order_rotation_turns(rotation: list[str]) -> Rotation:
    """Returns the list of turns in the following format:
    "A x SKILL > B x E. BASIC > C x BASIC" where A, B, and C are numbers of occurrences
    for skills, enhanced basic, and basic attacks respectively.
    These attacks are omitted if their occurrence equals 0."""

    skill_count = rotation.count("SKILL")
    e_basic_count = rotation.count("E. BASIC")
    basic_count = rotation.count("BASIC")
    num_turns = skill_count + e_basic_count + basic_count
    turns = []

    if skill_count > 1:
        turns.append(f"{skill_count} x SKILL")
    elif skill_count == 1:
        turns.append("SKILL")

    if e_basic_count > 1:
        turns.append(f"{e_basic_count} x E. BASIC")
    elif e_basic_count == 1:
        turns.append("E. BASIC")

    if basic_count > 1:
        turns.append(f"{basic_count} x BASIC")
    elif basic_count == 1:
        turns.append("BASIC")

    rotation_sequence = " > ".join(turns)

    return Rotation(rotation_sequence, skill_count,
                    e_basic_count, basic_count, num_turns)


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

    char_info = _get_char_info(energy_recharge, user_input)
    print(colored(char_info, "green"))

    print(f"Basic only rotation: {results.basic_rot} x BASIC")
    print(f"ER needed for the next breakpoint: {results.basic_er_threshold}%")
    print(f"Skill only rotation: {results.skill_rot} x SKILL")
    print(f"ER needed for the next breakpoint: {results.skill_er_threshold}%")

    if results.one_skill_rotation:
        print(f"One skill rotation: {results.one_skill_rotation}")

    if results.best_rotation:
        print(f"Most optimal rotation: "
              f"{results.best_rotation.sequence}\n")


def _get_char_info(energy_recharge: float, user_input: UserInput) -> str:
    """Collect's character info the user has input so that the user
    can more easily keep track of, and distinguish between,
    various calculation of the same character."""

    energy_recharge = round(energy_recharge * 100, 3)

    char_info = f"E{user_input.eidolons}"
    char_info += f" {user_input.char_name} with {energy_recharge}% ER"

    if LIGHT_CONES.get(user_input.light_cone):
        char_info += f" and S{user_input.superimposition + 1} {user_input.light_cone}"

    if user_input.ability != "--Character Ability--":
        char_info += f" and {user_input.ability}"

    return char_info


def print_results_blade(stats: CharStats,
                        user_input: UserInput, best_rotation: Rotation) -> None:
    """Specialized print function for Blade
    as his rotations include only enhanced basic attacks."""

    char_info = _get_char_info(stats.energy_recharge, user_input)
    print(colored(char_info, "green"))

    blade_breakpoint = get_er_breakpoint(best_rotation.e_basic_count, stats.e_basic,
                                         stats.ult_cost, stats.init_energy)

    print(f"Enchanted Basic rotation: {best_rotation.sequence}")
    print(f"ER needed for the next breakpoint: {blade_breakpoint}%\n")


def remove_permutations(list_of_lists):
    """Removes turn rotation permutations."""

    unique_tuples = {tuple(sorted(lst)) for lst in list_of_lists}
    unique_lists = [list(tpl) for tpl in unique_tuples]

    return unique_lists


def determine_initial_energy(stats: CharStats, user_input: UserInput):
    if user_input.assume_ult:
        stats.init_energy += stats.ult_act

    if user_input.num_ult_kills > 0:
        stats.init_energy += user_input.num_ult_kills * stats.ult_kill

    if user_input.num_follow_ups != "every turn" and user_input.num_follow_ups > 0:
        stats.init_energy += user_input.num_follow_ups * stats.follow_up

    if user_input.num_kills != "every turn" and user_input.num_kills > 0:
        stats.init_energy += user_input.num_kills * stats.kill

    if user_input.num_hits_taken != "every turn" and user_input.num_hits_taken > 0:
        stats.init_energy += user_input.num_hits_taken * stats.get_hit

    if user_input.num_relic_trigger != "every turn" and user_input.num_relic_trigger > 0:
        relic_energy = user_input.relic.recharge_value if user_input.relic else 0
        stats.init_energy += user_input.num_relic_trigger * relic_energy
