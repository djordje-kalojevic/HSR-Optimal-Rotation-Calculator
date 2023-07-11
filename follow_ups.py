"""Module for handling Follow-up attacks.

This module provides functionality for reading Light Cones talents from a CSV file,
storing them, as well as applying their bonuses."""

from dataclasses import dataclass
from csv import DictReader


LIGHT_CONES_CSV = "data/follow_up_attacks.csv"


@dataclass(frozen=True, slots=True)
class FollowUPAttack:
    """Dataclass that represents a Light Cone (LC).

    Attributes:
        - char_name: Name of the character.
        - energy_value: Amount of energy follow-up attack generates."""

    char_name: str
    energy_value: float


def _read_follow_ups_attacks() -> dict[str, FollowUPAttack]:
    """Reads the Light Cones from the CSV file and returns them as a dictionary.

    Returns:
        - Dictionary of LCs, where the keys are LC names,
        and the values are LC objects."""

    with open(LIGHT_CONES_CSV, "r", encoding="utf-8") as file:
        follow_up_attacks: dict[str, FollowUPAttack] = {}

        reader = DictReader(file)
        for row in reader:
            char_name = row["char_name"]
            energy_value = float(row["energy_value"])

            follow_up_attack = FollowUPAttack(char_name, energy_value)
            follow_up_attacks[char_name] = follow_up_attack

    return follow_up_attacks


FOLLOW_UP_ATTACKS = _read_follow_ups_attacks()
