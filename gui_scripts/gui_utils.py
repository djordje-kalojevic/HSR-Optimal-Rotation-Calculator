"""Module containing several functions for various GUI utilities."""

from typing import Optional
from qdarktheme import setup_theme
from darkdetect import isDark
from PyQt6.QtWidgets import QComboBox


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
    """Helper function to get an integer value from a combobox.
    Returns 0 if there was no selection."""

    try:
        return int(selector.currentText())
    except ValueError:
        return 0
