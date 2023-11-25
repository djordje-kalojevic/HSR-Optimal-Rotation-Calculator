"""Contains the UserInput dataclass, which store all user's GUI inputs."""

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Optional
from light_cones import LightCone
from relics import Relic
from talents import Talent
from .counter import Counter


@dataclass
class UserInput:
    """Contains all data user has inputted via the GUI."""

    char_name: str = ""
    eidolon_level: int = 0
    talent: Optional[Talent] = None
    num_talent_triggers = Counter()
    technique: bool = False
    trace: str = ""
    light_cone: Optional[LightCone] = None
    support_light_cone: Optional[LightCone] = None
    relic: Optional[Relic] = None
    num_relic_trigger = Counter()
    ornament: str = ""
    rope: str = ""
    num_hits_taken = Counter()
    ally_num_hits_taken = Counter()
    num_follow_ups = Counter()
    num_kills = Counter()
    num_ult_kills: int = 0
    assume_ult: bool = False
    assume_tingyun_ult: bool = False
    assume_tingyun_e6: bool = False
    detailed_breakdown: bool = False
    matching_enemy_weakness: bool = False
    enemy_count: int = 1
    huohuo_ult_level: int = 0
    _caches: dict[str, dict] = field(init=False, default_factory=dict)
    _counters: dict[str, Counter] = field(init=False, default_factory=dict)
    active_counters: bool | str = None

    def cache(self, cache_name) -> None:
        """Stores the current values of various counters,
        as they can get changed during calculation."""

        if not self._counters:
            self._counters = {attr_name: attr_value for attr_name, attr_value
                              in self.__dict__.items()
                              if isinstance(attr_value, Counter)}

        self._caches[cache_name] = deepcopy(self._counters)

    def retrieve_cache(self, cache_name) -> None:
        """Retrieves the stored user's inputs.
        Useful for reverting the changes made during the calculation,
        especially changes to the various counters."""

        if cache_name in self._caches:
            for attribute, value in self._caches[cache_name].items():
                setattr(self, attribute, value)

    def check_for_active_counters(self) -> None:
        """Checks whether there are any active counters.
        This is done to ensure that certain checks are not needlessly performed
        when there are no active counters."""

        if not self._counters:
            self._counters = {attr_name: attr_value for attr_name, attr_value
                              in self.__dict__.items()
                              if isinstance(attr_value, Counter)}

        for counter in self._counters.values():
            if counter.repeat_every_turn:
                self.active_counters = "every turn counter"
                return

        for counter in self._counters.values():
            if counter.num_triggers > 0:
                self.active_counters = True
                return

        self.active_counters = False
