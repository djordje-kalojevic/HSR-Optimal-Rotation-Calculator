from typing import Optional
from termcolor import colored
from characters import CharStats, HUOHUO_PERCENT_ENERGY_BONUSES
from gui_scripts.user_input import UserInput
from gui_scripts.counter import Counter
from traces import TRACES
from .rotation import Rotation


def determine_initial_energy(stats: CharStats, user_input: UserInput) -> float:
    """Determines the amount of energy character has before calculating their rotation.
    This can include the energy from activating their ultimate."""

    if user_input.assume_ult:
        stats.init_energy += stats.ult_act

    if user_input.num_ult_kills > 0:
        stats.init_energy += user_input.num_ult_kills * stats.ult_kill

    if user_input.huohuo_ult_level > 0:
        bonus = HUOHUO_PERCENT_ENERGY_BONUSES[user_input.huohuo_ult_level - 1]
        stats.init_energy += bonus / 100 * stats.ult_cost


def get_er_breakpoint(rotation: Rotation, attack_value: float,
                      ult_cost: float, init_energy: float) -> float:
    """Calculates and returns the energy recharge breakpoint, i.e.,
    how much more ER is required to shorten such a rotation by one turn.
    Return 0% if the rotation in question is 1 turn long,
    as there could not possibly exist a shorter rotation."""

    if rotation.num_turns - 1 == 0:
        return 0

    needed_attack_value = (ult_cost - init_energy) / (rotation.num_turns - 1)
    return round((needed_attack_value / attack_value - 1) * 100, 3)


def print_er_threshold(rotation: Rotation, stat_value: float,
                       ult_cost: float, init_energy: float) -> None:
    """Print the energy recharge needed for the next breakpoint."""

    er_threshold = get_er_breakpoint(rotation, stat_value,
                                     ult_cost, init_energy)
    if er_threshold > 0:
        print(f"ER needed for the next breakpoint: {er_threshold}%")


def find_basic_only_rotation(rotations: list[Rotation]) -> Optional[Rotation]:
    """Finds the shortest rotation that contains only basic attacks.
    Returns such a rotation if found, otherwise returns None."""

    try:
        basic_only_rotation = min((r for r in rotations
                                   if r.all_skills_count == 0),
                                  key=lambda r: (r.num_turns, -r.skill_points_generated))

        if basic_only_rotation:
            return basic_only_rotation
        return None

    except ValueError:
        return None


def find_skill_only_rotation(rotations: list[Rotation]) -> Optional[Rotation]:
    """Finds the shortest rotation that contains only skills.
    Returns such a rotation if found, otherwise returns None."""

    try:
        skill_only_rotation = min((r for r in rotations
                                   if r.all_basics_count == 0),
                                  key=lambda r: (r.num_turns, -r.skill_points_generated))
        if skill_only_rotation:
            return skill_only_rotation
        return None

    except ValueError:
        return None


def find_one_skill_rotation(rotations: list[Rotation]) -> Optional[Rotation]:
    """Finds the shortest rotation that contains only one skill.
    Returns such a rotation if found, otherwise returns None."""

    try:
        skill_only_rotation = min((r for r in rotations
                                   if r.all_skills_count == 1),
                                  key=lambda r: (r.num_turns, -r.skill_points_generated))
        if skill_only_rotation:
            return skill_only_rotation
        return None

    except ValueError:
        return None


def find_neutral_rotation(rotations: list[Rotation]) -> Optional[Rotation]:
    """Finds the shortest neutral rotation,
    i.e., a rotation that uses an average of 0 skill points per turn.
    Returns such a rotation if found, otherwise returns None."""

    try:
        skill_only_rotation = min((r for r in rotations
                                   if r.skill_points_generated == 0),
                                  key=lambda r: (r.num_turns))
        if skill_only_rotation:
            return skill_only_rotation
        return None

    except ValueError:
        return None


def find_best_rotation(rotations: list[Rotation]) -> Rotation:
    """Finds the best rotation, defined as the rotation with fewest turns,
    as well as the lowest skill point per turn cost."""

    best_rot = min(rotations,
                   key=lambda r: (r.num_turns, -r.skill_points_generated))

    return best_rot


def print_char_info(energy_recharge: float, user_input: UserInput) -> None:
    """Collects and prints character to more easily keep track of,
    and distinguish between, various calculations of the same character.

    This includes:
        - Character's energy recharge
        - selected eidolon level
        - equipped Light Cone and support Light Cone
        - selected trace"""

    energy_recharge = round(energy_recharge * 100, 3)
    char_info = f"E{user_input.eidolon_level} {user_input.char_name} with {energy_recharge}% ER"

    if user_input.light_cone:
        char_info += (f" and S{user_input.light_cone.superimposition + 1} "
                      f"{user_input.light_cone.name}")

    if user_input.support_light_cone:
        char_info += (f" and S{user_input.support_light_cone.superimposition + 1} "
                      f"{user_input.support_light_cone.name}")

    if user_input.trace in TRACES.keys():
        char_info += f" and {user_input.trace}"

    if user_input.technique:
        char_info += f" + technique"

    print(colored(char_info, "green"))


def print_rotation_info(rotation_name: str, rotation: Optional[Rotation], display_sp_cost=True) -> None:
    """Prints rotation info: name, energy generated, SP cost per turn, and turn sequence."""

    if not rotation:
        return

    if rotation_name == "Neutral rotation":
        display_sp_cost = False

    if display_sp_cost:
        print(f"{rotation_name} ({rotation.energy_generated} energy, "
              f"{rotation.sp_cost_per_turn} SP/T): {rotation.turn_sequence}")

    else:
        print(f"{rotation_name} ({rotation.energy_generated} energy): "
              f"{rotation.turn_sequence}")


def calculate_turn_energy(stats: CharStats, user_input: UserInput) -> float:
    """Calculates the energy generated during each turn based on user inputs.
    This includes follow-up attacks, kills, hits taken, ally hits taken,
    talents, and relic triggers."""

    if not user_input.active_counters:
        return 0
    elif user_input.active_counters != "every turn counter":
        user_input.check_for_active_counters()

    turn_energy = 0

    def process_action(trigger_counter: Counter, energy_bonus: float) -> Counter:
        nonlocal turn_energy
        if trigger_counter.num_triggers == 0 or energy_bonus == 0:
            return trigger_counter
        if trigger_counter.repeat_every_turn:
            turn_energy += energy_bonus * trigger_counter.num_triggers
        elif trigger_counter.num_triggers > 0:
            turn_energy += energy_bonus
            trigger_counter.num_triggers -= 1
        return trigger_counter

    # Process follow-up attacks
    user_input.num_follow_ups = process_action(user_input.num_follow_ups,
                                               stats.follow_up)

    # Process kills
    user_input.num_kills = process_action(user_input.num_kills, stats.kill)

    # Process getting hit
    user_input.num_hits_taken = process_action(user_input.num_hits_taken,
                                               stats.get_hit)
    # Process ally getting hit
    user_input.ally_num_hits_taken = process_action(user_input.ally_num_hits_taken,
                                                    stats.ally_get_hit)

    # Process relic bonuses
    if user_input.relic:
        relic_energy = user_input.relic.recharge_value
        user_input.num_relic_trigger = process_action(user_input.num_relic_trigger,
                                                      relic_energy)

    # Process talent bonuses
    if user_input.talent:
        user_input.num_talent_triggers = process_action(user_input.num_talent_triggers,
                                                        user_input.talent.energy)

    return turn_energy


def determine_ally_hit_energy(stats: CharStats, user_input: UserInput) -> None:
    """Checks if the character's condition for ally hit bonuses is True,
    if so calculates the bonus value."""

    # Character name, condition for ally hit bonus, bonus value
    ally_hit_bonuses: dict = {
        ("Clara", True):  5,
        ("Fu Xuan", user_input.eidolon_level >= 4): 5,
        ("Lynx", True): 2
    }

    stats.ally_get_hit = ally_hit_bonuses.get((user_input.char_name, True), 0)


def remove_duplicate_rotations(all_rotations: list[Rotation]) -> list[Rotation]:
    """Removes duplicates in order to speed up filters for various rotation types.
    Then returns the unique rotations."""

    unique_rotations = []
    seen_turn_combinations = set()

    for rotation in all_rotations:
        if rotation.turn_sequence not in seen_turn_combinations:
            seen_turn_combinations.add(rotation.turn_sequence)
            rotation.process_rotation_data()
            unique_rotations.append(rotation)

    return unique_rotations
