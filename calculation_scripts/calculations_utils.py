from dataclasses import dataclass, field
from typing import Optional
from characters import CharStats
from gui_scripts.gui_utils import UserInput


@dataclass(slots=True)
class Rotation:
    """Class representing a character rotation. It's attributes include:
    - the energy generated during it
    - turns that constitute it
    - its skill point cost
    - counters for all various attacks (basics, skills, enhanced basics etc.)"""

    energy_generated: float = 0
    turns: list[str] = field(default_factory=lambda: [])
    skill_point_generated: int = 0
    num_turns: int = 0
    sp_cost_per_turn: float = 0
    basic_count: int = 0
    skill_count: int = 0
    e_basic_count: int = 0
    e_basic_2_count: int = 0
    e_basic_3_count: int = 0
    e_skill_count: int = 0
    all_basics_count: int = 0
    all_skills_count: int = 0
    turn_sequence: str = ""

    def __post_init__(self):
        self.energy_generated = round(self.energy_generated, 3)
        self.num_turns = len(self.turns)
        self.sp_cost_per_turn = round(
            self.skill_point_generated / self.num_turns, 3)
        self.basic_count = self.turns.count("BASIC")
        self.skill_count = self.turns.count("SKILL")
        self.e_basic_count = (self.turns.count("E. BASIC")
                              + self.turns.count("EB1"))
        self.e_basic_2_count = self.turns.count("EB2")
        self.e_basic_3_count = self.turns.count("EB3")
        self.e_skill_count = self.turns.count("E. SKILL")
        self.all_basics_count = (self.basic_count + self.e_basic_count +
                                 self.e_basic_2_count + self.e_basic_3_count)
        self.all_skills_count = self.skill_count + self.e_skill_count
        self.turn_sequence = self._order_rotation_turns()

    def _order_rotation_turns(self) -> str:
        """Returns the list of turns in the following format:
        "A x SKILL > B x E. SKILL > C x E. BASIC > D x BASIC"
        where A, B, C, and D are numbers of occurrences for skills,
        enhanced skills, enhanced basic, and basic attacks respectively.
        These attacks are omitted if their occurrence equals 0."""

        sequence = []
        if self.skill_count > 1:
            sequence.append(f"{self.skill_count} x SKILL")
        elif self.skill_count == 1:
            sequence.append("SKILL")

        if self.e_skill_count > 1:
            sequence.append(f"{self.e_skill_count} x E. SKILL")
        elif self.e_skill_count == 1:
            sequence.append("E. SKILL")

        if self.e_basic_count > 1:
            sequence.append(f"{self.e_basic_count} x E. BASIC")
        elif self.e_basic_count == 1:
            sequence.append("E. BASIC")

        if self.basic_count > 1:
            sequence.append(f"{self.basic_count} x BASIC")
        elif self.basic_count == 1:
            sequence.append("BASIC")

        rotation_sequence = " > ".join(sequence)

        return rotation_sequence


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


def find_basic_only_rotation(rotations: list[Rotation]) -> Optional[Rotation]:
    """Finds the shortest rotation that contains only basic attacks.
    Returns such a rotation if found, otherwise returns None."""

    try:
        basic_only_rotation = min((r for r in rotations
                                   if r.all_skills_count == 0),
                                  key=lambda r: (r.num_turns, -r.skill_point_generated))
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
                                  key=lambda r: (r.num_turns, -r.skill_point_generated))
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
                                  key=lambda r: (r.num_turns, -r.skill_point_generated))
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
                                   if r.skill_point_generated == 0),
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
                   key=lambda r: (r.num_turns, -r.skill_point_generated))

    return best_rot


def get_char_info(energy_recharge: float, user_input: UserInput) -> str:
    """Collect's character info the user has input so that the user
    can more easily keep track of, and distinguish between,
    various calculations of the same character.

    This includes:
        - Character's energy recharge
        - selected eidolon level
        - equipped Light Cone and support Light Cone
        - selected ability"""

    energy_recharge = round(energy_recharge * 100, 3)
    char_info = f"E{user_input.eidolons} {user_input.char_name} with {energy_recharge}% ER"

    if user_input.light_cone:
        char_info += (f" and S{user_input.light_cone.superimposition + 1} "
                      f"{user_input.light_cone.name}")

    if user_input.support_light_cone:
        char_info += (f" and S{user_input.support_light_cone.superimposition + 1} "
                      f"{user_input.support_light_cone.name}")

    if user_input.ability != "--Character Ability--":
        char_info += f" and {user_input.ability}"

    return char_info


def determine_initial_energy(stats: CharStats, user_input: UserInput) -> float:
    """Determines the amount of energy character has before calculating their rotation.
    This can include the energy from activating their ultimate."""

    if user_input.assume_ult:
        stats.init_energy += stats.ult_act

    if user_input.num_ult_kills > 0:
        stats.init_energy += user_input.num_ult_kills * stats.ult_kill

    return stats.init_energy


def calculate_turn_energy(stats: CharStats, user_input: UserInput) -> float:
    """Calculates the energy generated during each turn based on user inputs.
    This includes follow-up attacks, kills, hits taken, and relic triggers."""

    turn_energy: float = 0

    if user_input.num_follow_ups == "every turn":
        turn_energy += stats.follow_up
    elif user_input.num_follow_ups > 0:
        turn_energy += stats.follow_up
        user_input.num_follow_ups -= 1

    if user_input.num_kills == "every turn":
        turn_energy += stats.kill
    elif user_input.num_kills > 0:
        turn_energy += stats.kill
        user_input.num_kills -= 1

    if user_input.num_hits_taken == "every turn":
        turn_energy += stats.get_hit
    elif user_input.num_hits_taken > 0:
        turn_energy += stats.get_hit
        user_input.num_hits_taken -= 1

    relic_energy = user_input.relic.recharge_value if user_input.relic else 0
    if user_input.num_relic_trigger == "every turn":
        turn_energy += relic_energy
    elif user_input.num_relic_trigger > 0:
        turn_energy += relic_energy
        user_input.num_relic_trigger -= 1

    ally_hit_energy = _get_ally_hit_energy(stats, user_input)
    if ally_hit_energy == 0:
        return turn_energy

    if user_input.ally_num_hits_taken == "every turn":
        turn_energy += ally_hit_energy
    elif user_input.ally_num_hits_taken > 0:
        turn_energy += ally_hit_energy
        user_input.ally_num_hits_taken -= 1

    return turn_energy


def _get_ally_hit_energy(stats: CharStats, user_input: UserInput):

    if user_input.char_name == "Lynx":
        energy = 2 * stats.energy_recharge
    elif user_input.char_name == "Fu Xuan" and user_input.eidolons >= 4:
        energy = 5 * stats.energy_recharge
    else:
        return 0

    return energy
