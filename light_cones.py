"""Module for handling Light Cones.

This module provides functionality for reading Light Cones from a CSV file,
storing them, as well as applying their bonuses."""

from csv import DictReader
from characters import CharStats
from dataclasses import dataclass, field
from gui_scripts.counter import Counter


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
    bonus: float = 0
    energy_values: list[float] = field(default_factory=lambda: [])
    triggered: bool = False
    trigger = Counter()

    def update_lc_bonus(self) -> None:
        self.bonus = self.energy_values[self.superimposition]


LIGHT_CONES_CSV = "data/light_cones.csv"


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


def apply_light_cones(stats: CharStats, user_input) -> None:
    """Applies Light Cone bonuses to the character's stats.

    Args:
        - stats: Character's stats to be modified.
        - light_cone_name: Name of the LC.
        - superimposition: Superimposition rank of the LC."""

    if user_input.light_cone:
        apply_light_cone_bonus(stats, user_input)

    if (user_input.support_light_cone and
            user_input.support_light_cone.recharge_type == "battle_start"):
        stats.init_energy += user_input.support_light_cone.bonus


def apply_light_cone_bonus(stats: CharStats, user_input) -> None:
    lc_bonus = user_input.light_cone.bonus

    match user_input.light_cone.recharge_type:
        case "energy_recharge":
            stats.energy_recharge += lc_bonus / 100
        case "battle_start":
            stats.init_energy += lc_bonus
        case "skill":
            stats.skill += lc_bonus
        case "attack":
            _apply_on_attack_bonus(stats, lc_bonus)
        case "attack_or_get_hit":
            _apply_on_attack_or_get_hit_bonus(stats, lc_bonus)
        case "echoes_coffin":
            _apply_echoes_coffin_bonus(stats, user_input)


def _apply_on_attack_bonus(stats: CharStats, lc_bonus: float) -> None:
    """Applies bonuses provided by attack-based Light Cones."""

    stats.basic += lc_bonus
    if stats.is_skill_attack:
        stats.skill += lc_bonus * stats.is_skill_attack
    if stats.is_ult_attack:
        stats.ult_act += lc_bonus * stats.is_ult_attack


def _apply_on_attack_or_get_hit_bonus(stats: CharStats, lc_bonus: float) -> None:
    """Applies bonuses provided by Light Cones, triggered by attacking or getting hit."""

    _apply_on_attack_bonus(stats, lc_bonus)
    stats.get_hit += lc_bonus


def _apply_echoes_coffin_bonus(stats: CharStats, user_input) -> None:
    """Applies bonuses offered by the Echoes of the Coffin Light Cone.
    It provides bonus energy based on the number of enemies hit, capping at 3."""

    lc_bonus = user_input.light_cone.bonus

    stats.basic += lc_bonus
    if stats.is_skill_attack:
        stats.skill += lc_bonus
    if stats.is_ult_attack and user_input.char_name == "Luocha":
        count = min(user_input.enemy_count, 3)
        stats.ult_act += count * lc_bonus
    elif stats.is_ult_attack:
        stats.ult_act += lc_bonus


LIGHT_CONES = _read_light_cones()
