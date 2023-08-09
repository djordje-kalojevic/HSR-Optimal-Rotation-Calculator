from dataclasses import dataclass
from csv import DictReader

CHARACTERS_CSV = "data/characters.csv"


@dataclass(frozen=True, slots=True)
class Character:
    name: str
    path: str
    ult_cost: int
    is_skill_attack: bool
    is_ult_attack: bool


@dataclass(slots=True)
class CharStats:
    """Contains default character values, relating to energy generation."""

    ult_cost: float
    energy_recharge: float = 1
    basic: float = 20
    skill: float = 30
    e_basic: float = 0
    follow_up: float = 0
    get_hit: float = 10
    kill: float = 10
    ult_kill: float = 10
    ult_act: float = 5
    init_energy: float = 0
    is_skill_attack: bool = False
    is_ult_attack: bool = False

    def apply_energy_recharge(self):
        stats_to_update = ['basic', 'skill', 'e_basic', 'follow_up', 'get_hit',
                           'kill', 'ult_kill', 'ult_act', 'init_energy']

        for stat in stats_to_update:
            current_val = getattr(self, stat)
            setattr(self, stat, current_val * self.energy_recharge)


def _read_characters() -> dict[str, Character]:
    with open(CHARACTERS_CSV, "r") as file:
        characters: dict[str, Character] = {}

        reader = DictReader(file)
        for row in reader:
            character = Character(
                row["name"],
                row["path"],
                int(row["ult_cost"]),
                bool(row["is_skill_attack"]),
                bool(row["is_ult_attack"]))

            characters[row["name"]] = character

    return characters


CHARACTERS = _read_characters()
# only supports characters which have had their ult costs revealed
SUPPORTED_CHARACTERS = [char.name for char in CHARACTERS.values()
                        if char.ult_cost > 0]
