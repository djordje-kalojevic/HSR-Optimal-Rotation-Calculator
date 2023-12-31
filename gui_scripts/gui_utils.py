"""Module containing several functions for various GUI utilities."""

from qdarktheme import setup_theme
from PyQt6.QtWidgets import QComboBox


def configure_theme() -> None:
    """Configures the program's dark theme.
    Includes fixes for barely visible tooltip text in the dark theme."""

    setup_theme(theme="dark",
                additional_qss="QToolTip {color: black; font-size: 13px}")


def get_int_from_selector(selector: QComboBox) -> int:
    """Helper function to get an integer value from a combobox.
    Returns 0 if there was no selection."""

    try:
        return int(selector.currentText())
    except ValueError:
        return 0
