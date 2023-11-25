from dataclasses import dataclass
from PyQt6.QtWidgets import QGridLayout, QPushButton


@dataclass
class ButtonLayout(QGridLayout):
    """Button layout with buttons for confirmation of all inputs,
    and button for refreshing the window, that is,
    for resetting all input value to their default values."""

    def __init__(self, parent):
        super().__init__()

        self.confirm_button = QPushButton("Confirm Selection")
        self.confirm_button.clicked.connect(parent.confirm_selection)
        self.confirm_button.setEnabled(False)

        self.reset_button = QPushButton("Reset Window")
        self.reset_button.clicked.connect(parent.refresh_window)
        self.addWidget(self.reset_button, 100, 0)
        self.addWidget(self.confirm_button, 100, 1)
