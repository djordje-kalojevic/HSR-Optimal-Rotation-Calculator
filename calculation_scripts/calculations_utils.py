from typing import Callable, Optional
from termcolor import colored
from character_utils.characters import CharStats
from character_utils.traces import TRACES
from gui_scripts.user_input import UserInput
from gui_scripts.counter import Counter
from .rotation import Rotation, RotationList


def determine_initial_energy(stats: CharStats, user_input: UserInput) -> None:
    """Determines the amount of energy character has before calculating their rotation.
    This can include the energy from activating their Ultimates."""

    if user_input.char_name == "Argenti":
        if user_input.assume_ult:
            enemy_hit_bonus = 3
            stats.init_energy += enemy_hit_bonus * user_input.enemy_count
        if user_input.technique:
            stats.init_energy += 15

    elif user_input.char_name == "Dr. Ratio" and user_input.assume_ult:
        stats.init_energy += 2 * stats.follow_up + stats.follow_up
        if user_input.eidolon_level == 6:
            stats.init_energy += stats.follow_up

    elif user_input.char_name == "Himeko":
        stats.ult_kill += 5

    elif user_input.char_name == "Ruan Mei" and user_input.technique:
        stats.init_energy += stats.skill

    if user_input.assume_ult:
        stats.init_energy += stats.ult_act

    if user_input.num_ult_kills > 0:
        stats.init_energy += user_input.num_ult_kills * stats.ult_kill


def find_basic_only_rotation(rotations: RotationList) -> Optional[Rotation]:
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


def find_skill_only_rotation(rotations: RotationList) -> Optional[Rotation]:
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


def find_one_skill_rotation(rotations: RotationList) -> Optional[Rotation]:
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


def find_neutral_rotation(rotations: RotationList) -> Optional[Rotation]:
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


def find_best_rotation(rotations: RotationList) -> Rotation:
    """Finds the best rotation, defined as the rotation with fewest turns,
    as well as the lowest skill point per turn cost."""

    best_rot = min(rotations,
                   key=lambda r: (r.num_turns, -r.skill_points_generated))

    return best_rot


def print_char_info(stats: CharStats, user_input: UserInput) -> None:
    """Collects and prints character to more easily keep track of,
    and distinguish between, various calculations of the same character.

    This includes:
        - Character's energy recharge
        - selected character's Eidolon level
        - equipped Light Cone and support Light Cone
        - selected character's Trace
        - selected character's technique"""

    char_info = ""
    energy_recharge = round(stats.energy_recharge * 100, 3)

    if user_input.char_name == "Argenti":
        char_info = f"{stats.ult_cost} energy mode: "

    char_info += (f"E{user_input.eidolon_level} {user_input.char_name} "
                  f"with {energy_recharge}% ER")

    if user_input.light_cone:
        char_info += (f" and S{user_input.light_cone.superimposition + 1} "
                      f"{user_input.light_cone.name}")

    if user_input.support_light_cone:
        char_info += (f" and S{user_input.support_light_cone.superimposition + 1} "
                      f"{user_input.support_light_cone.name}")

    if user_input.trace in TRACES.keys():
        trace_unlock_level = user_input.trace.split("(")[1][:-1]
        char_info += f" and {trace_unlock_level}"

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


def calculate_turn_energy(user_input: UserInput) -> float:
    """Calculates and returns the energy generated during each turn based on user inputs.
    This includes follow-up attacks, kills, hits taken, ally hits taken,
    talents, and relic triggers."""

    if not user_input.active_counters:
        return 0
    elif user_input.active_counters != "every turn counter":
        user_input.check_for_active_counters()

    turn_energy = 0

    def process_action(counter: Counter) -> None:
        nonlocal turn_energy
        if not counter or counter.num_triggers == 0 or counter.energy == 0:
            return
        if counter.repeat_every_turn:
            turn_energy += counter.energy * counter.num_triggers
        elif counter.num_triggers > 0:
            turn_energy += counter.energy
            counter.num_triggers -= 1

    for counter in user_input.counters.values():
        process_action(counter)

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


def print_er_breakpoint(function: Callable[[RotationList], Rotation],
                        algorithm: Callable[[CharStats, UserInput], RotationList],
                        all_rotations: RotationList,
                        old_rotation: Rotation,
                        stats: CharStats, user_input: UserInput,
                        old_er: float, upper_bound=2) -> None:
    """Uses a Binary Search Algorithm to calculate and print the Energy Recharge breakpoint,
    i.e., the amount of ER required to shorten such a rotation by one turn.
    If total ER needed is higher than 200%, Binary Search will not be performed,
    as there is no way to reach this much ER, as of now."""

    if not user_input.show_er_breakpoints or not old_rotation or old_rotation.num_turns == 1:
        return

    lower_bound = old_er
    precision = 0.00001

    stats.apply_energy_recharge(upper_bound)
    user_input.check_for_active_counters()

    all_rotations = algorithm(stats, user_input)
    new_rotation = function(all_rotations)

    if new_rotation and old_rotation.turn_sequence == new_rotation.turn_sequence:
        max_er = round(upper_bound * 100, 3)
        print(f"Total ER needed for the next breakpoint: >{max_er}%")
        stats.retrieve_cache("before-er-application", delete_cache=False)
        stats.apply_energy_recharge(old_er)
        return

    while abs(upper_bound-lower_bound) >= precision:
        mid_point = (upper_bound + lower_bound) / 2
        new_er = mid_point

        user_input.retrieve_cache("before-calculation")
        user_input.check_for_active_counters()
        stats.retrieve_cache("before-er-application", delete_cache=False)
        stats.apply_energy_recharge(new_er)

        all_rotations = algorithm(stats, user_input)
        new_rotation = function(all_rotations)

        if new_rotation and old_rotation.turn_sequence == new_rotation.turn_sequence:
            lower_bound = mid_point

        else:
            upper_bound = mid_point

    stats.retrieve_cache("before-er-application", delete_cache=False)
    stats.apply_energy_recharge(old_er)

    er_diff = round((new_er - old_er) * 100, 3)
    print(f"ER needed for the next breakpoint: {er_diff}%")


def determine_counter_energy_values(stats: CharStats, user_input: UserInput) -> None:
    """Determines and saves energy gained through various actions."""

    if user_input.talent:
        user_input.talent_triggers.energy = user_input.talent.energy
    if user_input.relic:
        user_input.relic_trigger.energy = user_input.relic.recharge_value

    user_input.hits_taken.energy = stats.get_hit
    user_input.ally_hits_taken.energy = stats.ally_get_hit
    user_input.follow_ups.energy = stats.follow_up
    user_input.kills.energy = stats.kill


def derive_special_action_values(stats: CharStats, user_input: UserInput) -> None:
    """Determines energy of Special, character-specific attacks,
    such as various Enhanced Basic Attacks, and Enhanced Skills."""

    match user_input.char_name:
        case "Argenti":
            enemy_hit_bonus = 3
            stats.basic += enemy_hit_bonus
            stats.skill += enemy_hit_bonus * user_input.enemy_count

        case "Blade":
            stats.e_basic = stats.basic + 10

        case "Dan Heng IL":
            stats.e_basic = stats.basic + 10
            stats.e_basic_2 = stats.basic + 15
            stats.e_basic_3 = stats.basic + 20

        case "Fu Xuan":
            stats.e_skill = stats.skill + 20

        case "Jingliu":
            stats.e_skill = stats.skill
            stats.skill -= 10

        case "Luka":
            stats.e_basic = stats.basic

        case "Trailblazer (Preservation)":
            stats.e_basic = stats.basic + 10
