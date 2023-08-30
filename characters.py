from dataclasses import dataclass, field
from csv import DictReader

CHARACTERS_CSV = "data/characters.csv"


@dataclass(slots=True)
class Character:
    name: str
    path: str
    ult_cost: int
    is_skill_attack: bool
    is_ult_attack: bool
    has_technique: bool


@dataclass
class CharStats:
    """Contains default character values, relating to energy generation."""

    ult_cost: float
    energy_recharge: float = 1
    basic: float = 20
    skill: float = 30
    e_basic: float = 0
    e_basic_2: float = 0
    e_basic_3: float = 0
    e_skill: float = 0
    follow_up: float = 0
    get_hit: float = 10
    kill: float = 10
    ult_kill: float = 10
    ult_act: float = 5
    init_energy: float = 0
    is_skill_attack: bool = False
    is_ult_attack: bool = False
    _caches: dict[str, dict] = field(init=False, default_factory=dict)

    def apply_energy_recharge(self, energy_recharge: float):
        """Applies energy recharge to all energy generating stats."""
        self.energy_recharge = energy_recharge
        stats_to_update = ["basic", "skill", "e_basic", "e_basic_2",
                           "e_basic_3", "e_skill", "follow_up", "get_hit",
                           "kill", "ult_kill", "ult_act", "init_energy"]

        for stat in stats_to_update:
            current_val = getattr(self, stat)
            setattr(self, stat, current_val * self.energy_recharge)

    def cache(self, cache_name):
        """Stores the current values of all character stats.
        Useful for applying temporary buffs."""
        if cache_name not in self._caches:
            self._caches[cache_name] = self.__dict__.copy()

    def retrieve_cache(self, cache_name):
        """Retrieves the stored character stats.
        Useful for taking away temporary buffs."""
        if cache_name in self._caches:
            for key, value in self._caches[cache_name].items():
                setattr(self, key, value)
            self._caches.pop(cache_name)


def _read_characters() -> dict[str, Character]:
    with open(CHARACTERS_CSV, "r", encoding="utf-8") as file:
        characters: dict[str, Character] = {}

        reader = DictReader(file)
        for row in reader:
            character = Character(
                row["name"],
                row["path"],
                int(row["ult_cost"]),
                bool(row["is_skill_attack"]),
                bool(row["is_ult_attack"]),
                bool(row["has_technique"]))

            characters[row["name"]] = character

    return characters


CHARACTERS = _read_characters()
# only supports characters which have had their ult costs revealed
SUPPORTED_CHARACTERS = [char.name for char in CHARACTERS.values()
                        if char.ult_cost > 0]
