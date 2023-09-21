"""Module for handling Light Cones.

This module provides functionality for reading Light Cones from a CSV file,
storing them, as well as applying their bonuses."""

from dataclasses import dataclass, field
from csv import DictReader
from typing import Optional, Literal
from characters import CharStats


LIGHT_CONES_CSV = "data/light_cones.csv"


@dataclass(slots=True)
class LightCone:
    """Dataclass that represents a Light Cone (LC).

    Attributes:
        - name: Name of the LC.
        - path: LC's path, i.e., which character's can get its bonus.
        - rarity: LC's rarity.
        - is_event_reward: Check whether the LC is an event reward or not.
        - recharge_type: Represents the type of the bonus LC provides.
        - superimposition: Superimposition rank of the LC."""

    name: str = ""
    path: str = ""
    rarity: str = ""
    is_support_lc: bool = False
    is_event_reward: bool = False
    recharge_type: str = ""
    superimposition: int = 0
    energy_values: list[float] = field(default_factory=lambda: [])
    triggered: bool = False
    num_triggers: int | Literal["every turn"] = 0


def _read_light_cones() -> dict[str, LightCone]:
    """Reads the Light Cones from the CSV file and returns them as a dictionary.

    Returns:
        - Dictionary of LCs, where the keys are LC names,
        and the values are LC objects."""

    with open(LIGHT_CONES_CSV, "r", encoding="utf-8") as file:
        light_cones: dict[str, LightCone] = {}

        reader = DictReader(file)
        for row in reader:
            light_cone = LightCone(
                name=row["name"],
                path=row["path"],
                rarity=row["rarity"],
                is_support_lc=bool(row["is_support_lc"]),
                is_event_reward=bool(row["is_event_reward"]),
                recharge_type=row["recharge_type"],
                energy_values=[float(row[f"Superimposition {i}"]) for i in range(1, 6)])

            light_cones[row["name"]] = light_cone

    return light_cones


def apply_light_cones(stats: CharStats, light_cone: Optional[LightCone],
                      support_light_cone: Optional[LightCone]):
    """Applies Light Cone bonuses to the character's stats.

    Args:
        - stats: Character's stats to be modified.
        - light_cone_name: Name of the LC.
        - superimposition: Superimposition rank of the LC."""

    if light_cone:
        apply_light_cone_bonus(stats, light_cone)

    if support_light_cone and support_light_cone.recharge_type == "battle_start":
        apply_battle_start_support_lc(stats, support_light_cone)


def apply_light_cone_bonus(stats: CharStats, light_cone: LightCone):
    lc_bonus = light_cone.energy_values[light_cone.superimposition]
    recharge_type = light_cone.recharge_type

    if recharge_type == "energy_recharge":
        stats.energy_recharge += lc_bonus / 100

    elif recharge_type == "battle_start":
        stats.init_energy += lc_bonus

    elif recharge_type == "attack":
        stats.basic += lc_bonus
        if stats.is_skill_attack:
            stats.skill += lc_bonus
        if stats.is_ult_attack:
            stats.ult_act += lc_bonus

    elif recharge_type == "skill":
        stats.skill += lc_bonus

    elif recharge_type == "attack_or_hit":
        stats.basic += lc_bonus
        if stats.is_skill_attack:
            stats.skill += lc_bonus
        if stats.is_ult_attack:
            stats.ult_act += lc_bonus
        stats.get_hit += lc_bonus

    elif recharge_type == "echoes_coffin":
        stats.basic += lc_bonus
        stats.ult_act += 2 * lc_bonus


def apply_battle_start_support_lc(stats: CharStats, support_light_cone: LightCone):
    stats.init_energy += support_light_cone.energy_values[
        support_light_cone.superimposition]


LIGHT_CONES = _read_light_cones()
