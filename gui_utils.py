from dataclasses import dataclass
from typing import Literal, Optional
from qdarktheme import setup_theme
from darkdetect import isDark
from relics import Relic


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
        setup_theme("light", additional_qss="QToolTip {font-size: 14px}")


@dataclass(slots=True)
class UserInput:
    """Contains all data user has inputted via the GUI."""

    char_name: str
    eidolons: int
    talent_level: int
    ability: str
    light_cone: str
    superimposition: int
    relic: Optional[Relic]
    num_relic_trigger: int | Literal["every turn"]
    ornament: str
    rope: str
    num_hits_taken: int | Literal["every turn"]
    num_follow_ups: int | Literal["every turn"]
    num_kills: int | Literal["every turn"]
    num_ult_kills: int
    assume_ult: bool
    assume_tingyun_ult: bool
    assume_tingyun_e6: bool
