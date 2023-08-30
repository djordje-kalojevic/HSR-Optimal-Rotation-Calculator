"""Module for handling relics.

This module provides functionality for reading relics from a CSV file,
storing them, as well as applying their bonuses."""

from dataclasses import dataclass
from csv import DictReader
from characters import CharStats


RELICS_CSV = "data/relics.csv"


@dataclass(slots=True)
class Relic:
    """Dataclass that represents a relic.

    Attributes:
        - name: Relic's name.
        - relic_type: Type of the relic.
        - recharge_type: Type of the effect relic provides.
        - recharge_value: Amount of energy relic provides."""

    name: str
    relic_type: str
    recharge_type: str
    recharge_value: float


def apply_rope(stats: CharStats, rope_rarity: str):
    """Applies rope bonuses to the character's stats.

    Args:
        - stats: Character's stats to be modified.
        - rope_rarity: Rarity of the rope to be applied."""

    rope = ALL_RELICS.get(rope_rarity)

    if rope:
        stats.energy_recharge += rope.recharge_value / 100


def apply_ornament(stats: CharStats, ornament_name: str):
    """Applies ornament bonuses to the character's stats.

    Args:
        - stats: Character's stats to be modified.
        - ornament_name: Name of the ornament to be applied."""

    ornament = ALL_RELICS.get(ornament_name)

    if ornament:
        stats.energy_recharge += ornament.recharge_value / 100


def _read_relics() -> dict[str, Relic]:
    """Reads all relic types from the CSV file and returns them as a dictionary.

    Returns:
        - Dictionary of relics, where the keys are relic names,
        and the values are Relic objects."""

    with open(RELICS_CSV, "r", encoding="utf-8") as file:
        all_relics: dict[str, Relic] = {}

        reader = DictReader(file)
        for row in reader:
            relic = Relic(
                row["name"],
                row["relic_type"],
                row["recharge_type"],
                float(row["recharge_value"])
            )
            all_relics[row["name"]] = relic

    return all_relics


ALL_RELICS = _read_relics()
RELICS = [r.name for r in ALL_RELICS.values() if r.relic_type == "relic"]
ORNAMENTS = [o.name for o in ALL_RELICS.values() if o.relic_type == "ornament"]
ROPES = [r.name for r in ALL_RELICS.values() if r.relic_type == "rope"]
