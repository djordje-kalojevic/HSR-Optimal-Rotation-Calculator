"""Contains the UserInput dataclass, which store all user's GUI inputs."""

from dataclasses import dataclass, field
from typing import Optional
from equipment_utils.light_cone import LightCone
from equipment_utils.relic import Relic
from character_utils.talents import Talent
from .counter import Counter


@dataclass
class UserInput:
    """Contains all data user has inputted via the GUI."""

    char_name: str = ""
    eidolon_level: int = 0
    talent: Optional[Talent] = None
    talent_triggers = Counter()
    technique: bool = False
    trace: str = ""
    light_cone: Optional[LightCone] = None
    support_light_cone: Optional[LightCone] = None
    relic: Optional[Relic] = None
    relic_trigger = Counter()
    ornament: str = ""
    rope: str = ""
    hits_taken = Counter()
    ally_hits_taken = Counter()
    follow_ups = Counter()
    kills = Counter()
    num_ult_kills: int = 0
    assume_ult: bool = False
    assume_tingyun_ult: bool = False
    assume_tingyun_e6: bool = False
    detailed_breakdown: bool = False
    show_er_breakpoints: bool = True
    matching_enemy_weakness: bool = False
    enemy_count: int = 1
    huohuo_ult_level: int = 0
    counters: dict[str, Counter] = field(init=False, default_factory=dict)
    active_counters: bool | str = None

    def cache(self, cache_name: str) -> None:
        """Stores the current values of various counters,
        as they can get changed during calculation.\n
        At the moment, cache_name is there only to explain
        why counters are being cached."""

        for counter in self.counters.values():
            counter.cache()

    def retrieve_cache(self, cache_name: str) -> None:
        """Retrieves the stored user's inputs.
        Useful for reverting the changes made during the calculation,
        especially changes to the various counters."""

        for counter in self.counters.values():
            counter.retrieve_cache()

    def check_for_active_counters(self) -> None:
        """Checks whether there are any active counters.
        This is done to ensure that certain checks are not needlessly performed
        when there are no active counters."""

        if not self.counters:
            self.counters = {attr_name: attr_value for attr_name, attr_value
                             in self.__dict__.items()
                             if isinstance(attr_value, Counter)}

        for counter in self.counters.values():
            if counter.repeat_every_turn:
                self.active_counters = "every turn counter"
                return

        for counter in self.counters.values():
            if counter.num_triggers > 0:
                self.active_counters = True
                return

        self.active_counters = False
