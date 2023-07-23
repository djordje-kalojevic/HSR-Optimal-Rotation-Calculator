"""Module for handling Light Cones.

This module provides functionality for reading Light Cones from a CSV file,
storing them, as well as applying their bonuses."""

from dataclasses import dataclass
from csv import DictReader
from characters import CharStats


LIGHT_CONES_CSV = "data/light_cones.csv"


@dataclass(frozen=True, slots=True)
class LightCone:
    """Dataclass that represents a Light Cone (LC).

    Attributes:
        - name: Name of the LC.
        - path: LC's path, i.e., which character's can get its bonus.
        - rarity: LC's rarity.
        - is_event_reward: Check whether the LC is an event reward or not.
        - recharge_type: Represents the type of the bonus LC provides.
        - superimposition: Superimposition rank of the LC."""

    name: str
    path: str
    rarity: str
    is_event_reward: bool
    recharge_type: str
    superimpositions: list[float]


def apply_light_cone(stats: CharStats, light_cone_name: str, superimposition: int):
    """Applies Light Cone bonuses to the character's stats.

    Args:
        - stats: Character's stats to be modified.
        - light_cone_name: Name of the LC.
        - superimposition: Superimposition rank of the LC."""

    light_cone = LIGHT_CONES.get(light_cone_name)

    if not light_cone:
        return

    energy_value = light_cone.superimpositions[superimposition]
    recharge_type = light_cone.recharge_type

    if recharge_type == "ER":
        stats.energy_recharge += energy_value / 100

    elif recharge_type == "battle start":
        stats.init_energy += energy_value

    elif recharge_type == "attack":
        stats.basic += energy_value
        stats.skill += energy_value
        stats.ult_act += energy_value

    elif recharge_type == "skill":
        stats.skill += energy_value

    elif recharge_type == "attack or hit":
        stats.basic += energy_value
        stats.skill += energy_value
        stats.ult_act += energy_value
        stats.get_hit += energy_value

    elif recharge_type == "echoes_coffin":
        stats.basic += energy_value
        stats.ult_act += 2 * energy_value


def _read_light_cones() -> dict[str, LightCone]:
    """Reads the Light Cones from the CSV file and returns them as a dictionary.

    Returns:
        - Dictionary of LCs, where the keys are LC names,
        and the values are LC objects."""

    with open(LIGHT_CONES_CSV, "r", encoding="utf-8") as file:
        light_cones: dict[str, LightCone] = {}

        reader = DictReader(file)
        for row in reader:
            name = row["name"]
            path = row["path"]
            rarity = row["rarity"]
            is_event_reward = bool(row["is_event_reward"])
            recharge_type = row["recharge_type"]

            # Extract the superimposition levels from the columns
            superimpositions = [
                float(row[f"Superimposition {i}"]) for i in range(1, 6)]

            light_cone = LightCone(name, path, rarity, is_event_reward,
                                   recharge_type, superimpositions)
            light_cones[name] = light_cone

    return light_cones


LIGHT_CONES = _read_light_cones()
LIGHT_CONE_NAMES = [light_cone.name for light_cone in LIGHT_CONES.values()]
