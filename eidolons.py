"""Module for handling character Eidolons.

This module provides functionality for reading character Eidolons from a CSV file,
storing them, as well as applying their bonuses."""

from math import ceil, floor
from dataclasses import dataclass
from csv import DictReader
from characters import CharStats
from gui_scripts.gui_utils import UserInput


EIDOLONS_CSV = "data/eidolons.csv"


@dataclass(slots=True)
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


def apply_eidolons(stats: CharStats, user_input: UserInput) -> None:
    """Applies Eidolon bonuses to the character's stats.

    Args:
        - stats: Character's stats to be modified.
        - char_name: Name of the character.
        - eidolon_level: Level of the Eidolon to be applied."""

    if user_input.eidolons == 0:
        return

    applicable_eidolons = [e for e in EIDOLONS
                           if e.char_name == user_input.char_name
                           and e.eidolon_level <= user_input.eidolons]

    if not applicable_eidolons:
        return

    for eidolon in applicable_eidolons:
        energy_value = eidolon.energy_value
        eidolon_type = eidolon.eidolon_type

        if eidolon_type == "skill":
            stats.skill += energy_value

        elif eidolon_type == "energy_recharge":
            stats.energy_recharge += energy_value / 100

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
            if user_input.enemy_count == 1:
                stats.basic += energy_value
                stats.skill += energy_value
                stats.ult_act += energy_value
            else:
                # to prevent floor(1/2) = 0
                basic_enemy_count = max(1, floor(user_input.enemy_count / 2))
                stats.basic += basic_enemy_count * energy_value
                stats.skill += ceil(user_input.enemy_count / 2) * energy_value
                stats.ult_act += user_input.enemy_count * energy_value

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
