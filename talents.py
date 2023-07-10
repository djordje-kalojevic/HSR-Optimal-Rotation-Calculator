"""Module for handling character talents.

This module provides functionality for reading character talents from a CSV file,
storing them, as well as applying their bonuses."""

from dataclasses import dataclass
from csv import DictReader
from characters import CharStats


TALENTS_CSV = "data/talents.csv"


@dataclass(frozen=True, slots=True)
class Talent:
    """Dataclass that represents a character's talent.

    Attributes:
        - char_name: Name of the character.
        - talent_name: Name of the talent.
        - talent_levels: List of talent levels."""

    char_name: str
    talent_name: str
    talent_levels: list[float]


def apply_talents(stats: CharStats, char_name: str, talent_level: int) -> None:
    """Applies talent bonuses to the character's stats.

    Args:
        - stats: Character's stats to be modified.
        - char_name: Name of the character.
        - talent_level: Level of the talent to be applied."""

    talent = TALENTS.get(char_name)

    if not talent or talent_level == 0:
        return

    if talent.char_name == "Pela":
        additional_energy = talent.talent_levels[talent_level - 1]
        stats.basic += additional_energy
        stats.skill += additional_energy
        stats.ult_act += additional_energy


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

            # Extract the Talent levels from the columns
            talent_levels = [
                float(row[f"Level {i}"]) for i in range(1, 16)]

            talent = Talent(char_name, talent_name, talent_levels)

            talents[char_name] = talent

    return talents


TALENTS = _read_talents()
