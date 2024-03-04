"""Module for handling character talents.

This module provides functionality for reading character talents from a CSV file,
storing them, as well as applying their bonuses."""

from dataclasses import dataclass, field
from csv import DictReader
from typing import Optional
from .characters import CharStats
from .follow_ups import follow_up_attack_check


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
        """Calculates the amount of energy gained from activating character's talent.
        Certain characters gain the same amount of energy independent of talent's level."""

        if talent_level == 0 or talent_level > len(self.talent_levels):
            self.energy = self.talent_levels[0]
        else:
            self.energy = self.talent_levels[talent_level - 1]


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


def apply_talents(stats: CharStats, talent: Optional[Talent]):
    if not talent:
        return

    match talent.char_name:
        case "Clara":
            follow_up_attack_check(stats, talent.char_name)
            stats.get_hit += stats.follow_up
        case "Pela":
            stats.ult_act += talent.energy


TALENTS = _read_talents()
