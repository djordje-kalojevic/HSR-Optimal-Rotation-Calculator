"""Module for handling character talents.

This module provides functionality for reading character talents from a CSV file,
storing them, as well as applying their bonuses."""

from dataclasses import dataclass, field
from csv import DictReader


TALENTS_CSV = "data/talents.csv"


@dataclass(slots=True)
class Talent:
    """Dataclass that represents a character's talent.

    Attributes:
        - char_name: Name of the character.
        - talent_name: Name of the talent.
        - talent_levels: List of talent levels."""

    char_name: str = ""
    talent_name: str = ""
    talent_levels: list[float] = field(init=True, default_factory=list)
    level: int = 0
    energy: float = 0

    def calculate_energy(self, talent_level):
        if talent_level != 0:
            self.energy = self.talent_levels[talent_level - 1]
        else:
            self.energy = self.talent_levels[0]


def _read_talents() -> dict[str, Talent]:
    """Reads the talents from the CSV file and returns them as a dictionary.

    Returns:
        - Dictionary of talents, where the keys are character names,
        and the values are Talent objects."""

    with open(TALENTS_CSV, "r", encoding="utf-8") as file:
        talents: dict[str, Talent] = {}

        reader = DictReader(file)
        for row in reader:
            char_name = row["char_name"]
            talent_name = row["talent_name"]
            talent_levels = [row[f"Level {i}"] for i in range(1, 16)]
            talent_levels = [float(value) for value in talent_levels if value]
            talent = Talent(char_name, talent_name, talent_levels)

            talents[char_name] = talent

    return talents


TALENTS = _read_talents()
