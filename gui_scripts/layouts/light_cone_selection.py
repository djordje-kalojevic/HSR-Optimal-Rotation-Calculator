from dataclasses import dataclass
from PyQt6.QtWidgets import QGridLayout
from ..widgets import Combobox, SearchBox
from equipment_utils.light_cones import LIGHT_CONES


@dataclass
class LightConeSelectionLayout(QGridLayout):
    """Layout which is responsible for input of all parameters related to Light Cones,
    i.e., their name, and their superimposition rank."""

    def __init__(self, parent):
        super().__init__()

        lcs = [lc.name for lc in LIGHT_CONES.values() if not lc.is_support_lc]
        self.lc_selector = SearchBox(text="--Search Light Cone--",
                                     items=lcs)
        self.lc_selector.currentTextChanged.connect(self._set_default_si)
        self.lc_selector.currentTextChanged.connect(
            self._enable_superimposition)

        self.si_selector = Combobox(parent, text="--Superimposition Level--",
                                    items=[f"Superimposition {i}" for i in range(1, 6)])
        self.si_selector.setEnabled(False)

        self.addWidget(self.lc_selector, 3, 0)
        self.addWidget(self.si_selector, 3, 1)

    def _enable_superimposition(self) -> None:
        selected_lc = self.lc_selector.currentText()
        light_cone = LIGHT_CONES.get(selected_lc)

        if light_cone:
            self.si_selector.setEnabled(True)
        else:
            self.si_selector.reset_selection()
            self.si_selector.setEnabled(False)

    def _set_default_si(self) -> None:
        """Sets default (assumed) superimposition level based on the following:
            - if the Light Cone is a three star, max superimposition is assumed
            - if the Light Cone is an event reward, max superimposition is assumed
            - otherwise, minimum superimposition is assumed"""

        selected_lc = self.lc_selector.currentText()
        light_cone = LIGHT_CONES.get(selected_lc)

        if not light_cone:
            return

        if light_cone.rarity == "3*" or light_cone.is_event_reward:
            self.si_selector.setCurrentText("Superimposition 5")
        else:
            self.si_selector.setCurrentText("Superimposition 1")
