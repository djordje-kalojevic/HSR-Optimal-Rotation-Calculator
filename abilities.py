"""Module for handling character abilities.

This module provides functionality for reading character abilities from a CSV file,
storing them, as well as applying their bonuses."""

from dataclasses import dataclass
from csv import DictReader
from characters import CharStats


ABILITIES_CSV = "data/abilities.csv"


@dataclass(slots=True)
class Ability:
    """Dataclass that represents a character's ability.

    Attributes:
        - char_name: Name of the character.
        - name: Name of the ability.
        - type: Type of the bonus ability provides.
        - value_bonus: Value of the bonus the ability provides."""

    char_name: str
    name: str
    type: str
    value_bonus: int


def apply_abilities(stats: CharStats, name: str = "") -> None:
    """Applies ability bonuses to the character's stats.

    Args:
        - stats: Character's stats to be modified.
        - name: Name of the ability."""

    ability = ABILITIES.get(name)

    if not ability:
        return

    value_bonus = ability.value_bonus
    type = ability.type

    if type == "battle_start":
        stats.init_energy += value_bonus

    elif type == "turn":
        stats.basic += value_bonus
        stats.skill += value_bonus

    elif type == "ult_act":
        stats.ult_act += value_bonus

    elif type == "yukong_majestas":
        stats.skill += 2 * value_bonus


def _read_abilities() -> dict[str, Ability]:
    """Reads the abilities from the CSV file and returns them as a dictionary.

    Returns:
        - Dictionary of abilities, where the keys are ability names,
        and the values are Ability objects."""

    with open(ABILITIES_CSV, "r", encoding="utf-8") as file:
        abilities: dict[str, Ability] = {}

        reader = DictReader(file)
        for row in reader:
            char_name = row["char_name"]
            name = row["ability_name"]
            type = row["ability_type"]
            value_bonus = int(row["value"])

            ability = Ability(char_name, name,
                              type, value_bonus)
            abilities[name] = ability

    return abilities


ABILITIES = _read_abilities()
