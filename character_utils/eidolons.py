"""Module for handling character Eidolons.

This module provides functionality for reading character Eidolons from a CSV file,
storing them, as well as applying their bonuses."""

from math import ceil, floor
from dataclasses import dataclass
from csv import DictReader
from .characters import CharStats
from gui_scripts.user_input import UserInput


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

    if user_input.eidolon_level == 0:
        return

    applicable_eidolons = [e for e in EIDOLONS
                           if e.char_name == user_input.char_name
                           and e.eidolon_level <= user_input.eidolon_level]

    if not applicable_eidolons:
        return

    for eidolon in applicable_eidolons:
        _apply_eidolon(stats, user_input, eidolon)


def _apply_eidolon(stats: CharStats, user_input: UserInput, eidolon: Eidolon) -> None:
    """Applies the Eidolon's bonus based on the type of the bonus."""

    energy_value = eidolon.energy_value

    match eidolon.eidolon_type:
        case "energy_recharge":
            stats.energy_recharge += energy_value / 100
        case "follow-up":
            stats.follow_up += energy_value
        case "skill":
            stats.skill += energy_value
        case "get_hit":
            stats.get_hit += energy_value
        case "ult_act":
            stats.ult_act += energy_value
        case "kill":
            stats.kill += energy_value
        case "ult_kill":
            stats.ult_kill += energy_value
        case "yukong_e6":
            stats.ult_act += energy_value
        case "serval":
            _apply_serval_eidolon(stats, user_input, energy_value)
        case "lightning_lord":
            stats.skill += 2 * energy_value
            stats.ult_act += 3 * energy_value


def _apply_serval_eidolon(stats: CharStats, user_input: UserInput, energy_value: float) -> None:
    """Serval's Eidolon 2 provides bonus energy every time her talent is triggered, i.e.,
    every time she hits a shocked enemy. This includes:
        - Basic Attack max out at 2 stacks of her talent (minimum 1)
        - Skill max out at 3 stacks of her talent
        - Ultimate: max out at the number of enemies specified."""

    enemy_count = user_input.enemy_count

    if enemy_count == 1:
        stats.basic += energy_value
        stats.skill += energy_value
        stats.ult_act += energy_value
    else:
        stats.basic += max(1, floor(enemy_count / 2)) * energy_value
        stats.skill += ceil(enemy_count / 2) * energy_value
        stats.ult_act += enemy_count * energy_value


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
