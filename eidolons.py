"""Module for handling character Eidolons.

This module provides functionality for reading character Eidolons from a CSV file,
storing them, as well as applying their bonuses."""

from dataclasses import dataclass
from csv import DictReader
from characters import CharStats


EIDOLONS_CSV = "data/eidolons.csv"


@dataclass(frozen=True, slots=True)
class Eidolon:
    """Dataclass that represents a character's Eidolon.

    Attributes:
        - char_name: Name of the character.
        - eidolon_level: Level of the Eidolon.
        - eidolon_type: Type of the bonus Eidolon provides.
        - energy_value: Amount of energy or energy recharge Eidolon provides."""

    char_name: str
    eidolon_level: int
    eidolon_type: str
    energy_value: int


def apply_eidolons(stats: CharStats, char_name: str, eidolon_level: int) -> None:
    """Applies Eidolon bonuses to the character's stats.

    Args:
        - stats: Character's stats to be modified.
        - char_name: Name of the character.
        - eidolon_level: Level of the Eidolon to be applied."""

    if eidolon_level == 0:
        return

    applicable_eidolons = [e for e in EIDOLONS if e.char_name ==
                           char_name and e.eidolon_level <= eidolon_level]

    if not applicable_eidolons:
        return

    for eidolon in applicable_eidolons:
        energy_value = eidolon.energy_value
        eidolon_type = eidolon.eidolon_type

        if eidolon_type == "skill":
            stats.skill += energy_value

        elif eidolon_type == "energy_recharge":
            stats.energy_recharge += energy_value

        elif eidolon_type == "lightning_lord":
            stats.skill += 2 * energy_value
            stats.ult_act += 3 * energy_value

        elif eidolon_type == "ult_act":
            stats.ult_act += energy_value

        elif eidolon_type == "get_hit":
            stats.get_hit += energy_value

        elif eidolon_type == "kill":
            stats.kill += energy_value

        elif eidolon_type == "serval":
            stats.basic += energy_value
            stats.skill += 2 * energy_value
            stats.ult_act += 3 * energy_value

        elif eidolon_type == "ult_kill":
            stats.ult_kill += energy_value

        elif eidolon_type == "yukong_e6":
            stats.ult_act += 2


def _read_eidolons() -> list[Eidolon]:
    """Reads the Eidolons from the CSV file and returns them as a list.

    Returns:
        - List of Eidolons"""

    with open(EIDOLONS_CSV, "r", encoding="utf-8") as file:
        eidolons: list[Eidolon] = []

        reader = DictReader(file)
        for row in reader:
            char_name = row["char_name"]
            eidolon_level = int(row["eidolon_level"])
            eidolon_type = row["eidolon_type"]
            energy_value = int(row["energy_value"])

            eidolon = Eidolon(char_name, eidolon_level,
                              eidolon_type, energy_value)

            eidolons.append(eidolon)

    return eidolons


EIDOLONS = _read_eidolons()
