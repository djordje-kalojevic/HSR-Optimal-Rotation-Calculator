"""Module containing several functions for various GUI utilities.
Additionally contains the UserInput dataclass, which store all user's GUI inputs."""

from dataclasses import dataclass, field
from typing import Literal, Optional
from qdarktheme import setup_theme
from darkdetect import isDark
from PyQt6.QtWidgets import QComboBox
from typing import Literal, Optional
from light_cones import LightCone
from relics import Relic


@dataclass
class UserInput:
    """Contains all data user has inputted via the GUI."""

    char_name: str = ""
    eidolons: int = 0
    talent_level: int = 0
    technique: bool = False
    ability: str = ""
    light_cone: Optional[LightCone] = None
    support_light_cone: Optional[LightCone] = None
    relic: Optional[Relic] = None
    num_relic_trigger: int | Literal["every turn"] = 0
    ornament: str = ""
    rope: str = ""
    num_hits_taken: int | Literal["every turn"] = 0
    ally_num_hits_taken: int | Literal["every turn"] = 0
    num_follow_ups: int | Literal["every turn"] = 0
    num_kills: int | Literal["every turn"] = 0
    num_ult_kills: int = 0
    assume_ult: bool = False
    assume_tingyun_ult: bool = False
    assume_tingyun_e6: bool = False
    detailed_breakdown: bool = False
    matching_enemy_weakness: bool = False
    _caches: dict[str, dict] = field(init=False, default_factory=dict)

    def cache(self, cache_name):
        """Stores the current values of all user's inputs.
        Useful because these values, especially the various counters,
        can get changed during calculation."""
        if cache_name not in self._caches:
            self._caches[cache_name] = self.__dict__.copy()

    def retrieve_cache(self, cache_name):
        """Retrieves the stored user's inputs.
        Useful for reverting the changes made during the calculation,
        especially changes to the various counters."""
        if cache_name in self._caches:
            for key, value in self._caches[cache_name].items():
                setattr(self, key, value)
            self._caches.pop(cache_name)


def configure_theme(theme: Optional[str] = None) -> None:
    """Configures the program's theme based on the OS theme or an explicit overwrite value.
    Includes fixes for barely visible tooltip text in the dark theme.

    Args:
        - theme (str): Use "dark" or "light" to explicitly set the theme,
                       regardless of the OS theme."""

    if isDark() or theme == "dark":
        setup_theme("dark",
                    additional_qss="QToolTip {color: black; font-size: 13px}")
    else:
        setup_theme("light", additional_qss="QToolTip {font-size: 13px}")


def get_int_from_selector(selector: QComboBox) -> int:
    """Helper function to get an integer value from a combobox."""

    try:
        return int(selector.currentText())
    except ValueError:
        return 0


def get_int_or_literal_from_selector(selector: QComboBox) -> int | Literal["every turn"]:
    """Helper function to get an integer value or a literal.

    Returns:
        - int | Literal["every turn"]"""

    text = selector.currentText()
    if text == "every turn":
        return "every turn"

    try:
        return int(text)
    except ValueError:
        return 0
