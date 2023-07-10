"""An algorithm-based calculation for quickly calculating several important things:

    - Basic attack only rotation, and the required energy recharge for the next breakpoint.
    - Skill only rotation, and the needed energy recharge for the next breakpoint.
    - One-skill rotation, perfect for checking if your rotation aligns with buff/debuff durations.
    - Shortest, most skill-positive rotation, i.e.,
    it prioritizes rotations with the lowest skill point cost,
    if multiple rotations are eligible."""

from PyQt6.QtWidgets import QApplication
from gui import MainWindowDemo
from gui_utils import configure_theme

def main() -> None:
    """Calculator's main function which incorporates the GUI, as well as all the calculations."""

    app = QApplication([])
    configure_theme()
    dialog = MainWindowDemo()
    dialog.exec()


if __name__ == '__main__':
    main()
