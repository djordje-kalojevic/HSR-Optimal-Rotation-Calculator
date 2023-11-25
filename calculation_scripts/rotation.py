from dataclasses import dataclass, field


@dataclass(slots=True)
class Rotation:
    """Class representing a character rotation. It's attributes include:
    - the energy generated during it
    - turns that constitute it
    - its skill point cost
    - counters for all various attacks (basics, skills, enhanced basics etc.)"""

    energy_generated: float = 0
    turns: list[str] = field(default_factory=lambda: [])
    skill_points_generated: int = 0
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
        """Sorts turns and joins them into a temporary turn sequence
        for easier and faster filtering later on."""

        self.turns.sort()
        self.turn_sequence = " ".join(self.turns)

    def process_rotation_data(self) -> None:
        """Processes and computes attributes of the rotation.

        This method calculates and updates various attributes of the rotation,
        including the number of turns, energy generated,
        skill point cost per turn, and various attack counts.
        It also orders the rotation turns for easier analysis and filtering."""

        self.num_turns = max(len(self.turns), 1)
        self.energy_generated = round(self.energy_generated, 3)
        self.sp_cost_per_turn = round(
            self.skill_points_generated / self.num_turns, 3)
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

    def _order_rotation_turns(self) -> None:
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

        return " > ".join(sequence)
