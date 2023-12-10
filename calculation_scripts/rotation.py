"""Module containing Rotation and RotationList dataclasses,
used for storing character's rotation data."""

from dataclasses import dataclass, field
from typing import Optional
from rbloom import Bloom


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

    def process_rotation_data(self, char_name: Optional[str] = None) -> None:
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

        if char_name == "Dan Heng IL":
            self.turn_sequence = self._order_turns_dhil()
        else:
            self.turn_sequence = self._order_turns()

    def _order_turns(self) -> str:
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

    def _order_turns_dhil(self) -> str:
        """Returns the list of turns in the following format:
        "A x EB3 > B x EB2 > C x EB1 > D x BASIC" where A, B, C
        and D are numbers of occurrences for level 3 Enhanced Basics,
        level 2 EBs, level 1 EBs, and Basic attacks respectively.
        These attacks are omitted if their occurrence equals 0."""

        sequence = []

        if self.e_basic_3_count > 1:
            sequence.append(f"{self.e_basic_3_count} x EB3")
        elif self.e_basic_3_count == 1:
            sequence.append("EB3")

        if self.e_basic_2_count > 1:
            sequence.append(f"{self.e_basic_2_count} x EB2")
        elif self.e_basic_2_count == 1:
            sequence.append("EB2")

        if self.e_basic_count > 1:
            sequence.append(f"{self.e_basic_count} x EB1")
        elif self.e_basic_count == 1:
            sequence.append("EB1")

        if self.basic_count > 1:
            sequence.append(f"{self.basic_count} x BASIC")
        elif self.basic_count == 1:
            sequence.append("BASIC")

        return " > ".join(sequence)


@dataclass(slots=True)
class RotationList(list[Rotation]):
    """Custom class representing a list[Rotation].
    Mimics all built-in methods of a regular list class,
    with the added "add_rotation" which checks whether a rotation is unique,
    and if it is adds it to the RotationList itself."""

    bloom_filter = Bloom(1000, 0.001)

    def __post_init__(self):
        """Clears the Bloom Filter before every individual calculation.
        Otherwise the filter would get filled and no new rotations could be added,
        resulting in no results at all, and calculator failing."""

        self.bloom_filter.clear()

    def add_rotation(self, energy_generated: float, turns: list[str],
                     skill_points_generated: float) -> None:
        """Checks if the rotation is unique, i.e., not a permutation of another one.
        If so, Rotation dataclass is created and appended."""

        turn_sequence = " ".join(sorted(turns))

        if turn_sequence not in self.bloom_filter:
            self.bloom_filter.add(turn_sequence)
            self.append(Rotation(energy_generated, turns,
                                 skill_points_generated))

    def process_rotation_data(self, char_name: Optional[str] = None) -> None:
        """Processes and computes attributes of all stored rotations."""

        [rotation.process_rotation_data(char_name) for rotation in self]
