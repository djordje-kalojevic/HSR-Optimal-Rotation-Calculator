from dataclasses import dataclass
from typing import Optional
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (QDialog, QWidget, QLabel, QComboBox, QGridLayout,
                             QCheckBox, QFormLayout, QStyle, QPushButton, QHBoxLayout)
from characters import Character, CHARACTERS, SUPPORTED_CHARACTERS
from abilities import ABILITIES
from eidolons import EIDOLONS
from talents import TALENTS
from follow_ups import FOLLOW_UP_ATTACKS
from light_cones import LIGHT_CONE_NAMES, LIGHT_CONES, SUPPORT_LIGHT_CONES
from relics import RELICS, ORNAMENTS, ROPES


@dataclass
class Combobox(QComboBox):
    def __init__(self, parent, text="", items: Optional[list[str]] = None):
        super().__init__(parent)
        self.setPlaceholderText(text)
        if items:
            self.addItems(items)
        self.setMaxVisibleItems(20)
        self.clearEditText()


class Tooltip(QLabel):
    """A custom tooltip widget."""

    def __init__(self, parent=None, tooltip_text="", icon_size=QSize(16, 16)):
        super().__init__(parent)

        pixmap_name = QStyle.StandardPixmap.SP_MessageBoxQuestion
        pixmap = self.style().standardPixmap(pixmap_name)
        resized_pixmap = pixmap.scaled(icon_size,
                                       Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(resized_pixmap)
        self.setToolTip(tooltip_text)


@dataclass
class CheckBox(QWidget):
    """A custom widget for displaying a checkbox with tooltip."""

    def __init__(self, parent: QDialog, label: str,
                 tooltip_text: str, checked=False, icon_size=QSize(16, 16)) -> None:
        super().__init__(parent)

        form_layout = QFormLayout()
        self.checkbox = QCheckBox(label)
        self.checkbox.setChecked(checked)
        self.tooltip = Tooltip(parent, tooltip_text, icon_size)

        form_layout.addRow(self.checkbox, self.tooltip)
        self.setLayout(form_layout)


@dataclass
class CharSelectorLayout(QGridLayout):
    """Layout which is responsible for input of all parameters related to characters,
    i.e., their name, Eidolons, talents, abilities, and follow-up attacks."""

    def __init__(self, parent):
        super().__init__()

        self.char_selector = Combobox(
            parent, "--Select Character--", SUPPORTED_CHARACTERS)
        self.char_selector.currentTextChanged.connect(
            parent._get_compatible_lc)
        self.char_selector.currentTextChanged.connect(lambda:
                                                      self._enable_options(parent))
        self.char_selector.currentTextChanged.connect(
            parent._enable_confirm_button)

        self.eidolons_selector = Combobox(
            parent, items=["--Eidolon Level--"])
        self.eidolons_selector.setEnabled(False)

        self.ability_selector = Combobox(
            parent, items=["--Character Ability--"])
        self.ability_selector.setEnabled(False)

        self.talent_selector = Combobox(
            parent, items=["--Talent Level--"] + [f"{i}" for i in range(1, 16)])
        self.talent_selector.setEnabled(False)

        self.follow_up_selector = Combobox(
            parent, items=["--Follow-up Attacks--", "every turn",
                           "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        self.follow_up_selector.setEnabled(False)

        self.technique_check = CheckBox(
            parent, "Technique?",
            tooltip_text="Has this character's technique been used before combat?")
        self.technique_check.setEnabled(False)

        self.addWidget(self.char_selector, 1, 0)
        self.addWidget(self.eidolons_selector, 1, 1)
        self.addWidget(self.technique_check, 1, 2)
        self.addWidget(self.ability_selector, 2, 0)
        self.addWidget(self.talent_selector, 2, 1)
        self.addWidget(self.follow_up_selector, 2, 2)
        self.addWidget(QWidget(), 3, 0)

    def _enable_options(self, parent) -> None:
        char_name = self.char_selector.currentText()
        eidolon_level = self.eidolons_selector.currentText()
        char = CHARACTERS.get(char_name)
        if not char:
            return

        self._enable_ult_kills_input(parent, char)
        self._enable_char_ability(char_name)
        self._enable_char_eidolons(char_name)
        self._enable_char_talents(char_name)
        self._enable_follow_up_attacks(char_name)
        self._enable_technique_toggle(char)

    def _enable_ult_kills_input(self, parent, char: Character):
        options = parent.options_layout
        if char.is_ult_attack:
            options.ult_kills_input.setEnabled(True)

        else:
            options.ult_kills_input.setEnabled(False)
            options.ult_kills_input.setCurrentText("--Assume Ult kills--")

    def _enable_char_ability(self, char_name: str):
        char_ability = (["--Character Ability--"] + [a.name for a in ABILITIES.values()
                                                     if a.char_name == char_name])
        if len(char_ability) > 1:
            self.ability_selector.setEnabled(True)
            self.ability_selector.clear()
            self.ability_selector.addItems(char_ability)

        else:
            self.ability_selector.setEnabled(False)
            self.ability_selector.setCurrentText("--Character Ability--")

    def _enable_char_eidolons(self, char_name: str):
        self.eidolons_selector.setEnabled(True)
        char_eidolons = [str(e.eidolon_level) for e in EIDOLONS
                         if e.char_name == char_name]
        if char_eidolons:
            self.eidolons_selector.setEnabled(True)
            self.eidolons_selector.clear()
            self.eidolons_selector.addItems(
                ["--Eidolon Level--"] + char_eidolons)
        else:
            self.eidolons_selector.setEnabled(False)
            self.eidolons_selector.setCurrentText("--Eidolon Level--")

    def _enable_char_talents(self, char_name: str):
        if TALENTS.get(char_name):
            self.talent_selector.setEnabled(True)
        else:
            self.talent_selector.setEnabled(False)
            self.talent_selector.setCurrentText("--Talent Level--")

    def _enable_follow_up_attacks(self, char_name: str):
        # Blade's follow-ups are already included in his rotations
        if FOLLOW_UP_ATTACKS.get(char_name) and char_name != "Blade":
            self.follow_up_selector.setEnabled(True)
        else:
            self.follow_up_selector.setEnabled(False)
            self.follow_up_selector.setCurrentText("--Follow-up Attacks--")

    def _enable_technique_toggle(self, char: Character):
        if char.has_technique:
            self.technique_check.setEnabled(True)
        else:
            self.technique_check.setEnabled(False)


@dataclass
class LightConeSelectionLayout(QGridLayout):
    """Layout which is responsible for input of all parameters related to Light Cones,
    i.e., their name, and their superimposition rank."""

    def __init__(self, parent):
        super().__init__()

        self.lc_selector = Combobox(
            parent, items=["--Select Light Cone--"] + LIGHT_CONE_NAMES)
        self.lc_selector.currentTextChanged.connect(self._set_default_si)
        self.lc_selector.currentTextChanged.connect(
            self._enable_superimposition)

        self.si_selector = Combobox(parent, "--Superimposition Level--",
                                    ["Superimposition 1", "Superimposition 2",
                                     "Superimposition 3", "Superimposition 4",
                                     "Superimposition 5"])
        self.si_selector.setEnabled(False)

        self.addWidget(self.lc_selector, 3, 0)
        self.addWidget(self.si_selector, 3, 1)

    def _enable_superimposition(self) -> None:
        selected_lc = self.lc_selector.currentText()
        light_cone = LIGHT_CONES.get(selected_lc)

        if light_cone:
            self.si_selector.setEnabled(True)
        else:
            self.si_selector.setCurrentText("--Select Light Cone--")
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


@dataclass
class SupportLightConeSelectionLayout(QGridLayout):
    """Layout which is responsible for input of all parameters related to Light Cones,
    i.e., their name, and their superimposition rank."""

    def __init__(self, parent):
        super().__init__()

        self.lc_selector = Combobox(
            parent, items=["--Select Support Light Cone--"] + SUPPORT_LIGHT_CONES)
        self.lc_selector.currentTextChanged.connect(self._set_default_si)
        self.lc_selector.currentTextChanged.connect(
            self._enable_superimposition)

        self.si_selector = Combobox(parent, "--Superimposition Level--",
                                    ["Superimposition 1", "Superimposition 2",
                                     "Superimposition 3", "Superimposition 4",
                                     "Superimposition 5"])
        self.si_selector.setEnabled(False)
        self.trigger_input = Combobox(
            parent,
            items=["--Light Cone Triggers--", "every turn",
                   "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        self.trigger_input.setEnabled(False)

        self.addWidget(self.lc_selector, 3, 0, 1, 2)
        self.addWidget(self.si_selector, 3, 3)
        self.addWidget(self.trigger_input, 3, 4)

    def _enable_superimposition(self) -> None:
        selected_lc = self.lc_selector.currentText()
        light_cone = LIGHT_CONES.get(selected_lc)

        if light_cone:
            self.si_selector.setEnabled(True)
        else:
            self.si_selector.setCurrentText("--Select Support Light Cone--")
            self.si_selector.setEnabled(False)
            self.trigger_input.setCurrentText("--Light Cone Triggers--")
            self.trigger_input.setEnabled(False)

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

        if self.lc_selector.currentText() == "Fine Fruit":
            self.trigger_input.setCurrentText("--Light Cone Triggers--")
            self.trigger_input.setEnabled(False)
        else:
            self.trigger_input.setEnabled(True)


@dataclass
class RelicSelectionLayout(QGridLayout):
    """Layout which is responsible for input of all parameters related to all types of relics,
    i.e., regular relics, ornaments, and energy recharge ropes.
    Additionally, user can configure how many times relic effects are triggered."""

    def __init__(self, parent):
        super().__init__()

        self.relic_selector = Combobox(
            parent, "--Select Relic--", RELICS)
        self.relic_selector.currentTextChanged.connect(
            self._enable_relic_toggle)
        self.relic_trigger_input = Combobox(
            parent,
            items=["--Relic triggers--", "every turn",
                   "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        self.relic_trigger_input.setEnabled(False)

        self.ornament_selector = Combobox(
            parent, items=["--Select Ornament--"] + ORNAMENTS)

        self.rope_selector = Combobox(
            parent, items=["--Select ER rope--"] + ROPES)

        self.addWidget(self.relic_selector, 4, 0)
        self.addWidget(self.relic_trigger_input, 4, 1)
        self.addWidget(self.ornament_selector, 5, 0)
        self.addWidget(self.rope_selector, 5, 1)

    def _enable_relic_toggle(self) -> None:
        self.relic_trigger_input.setEnabled(True)


@dataclass
class OptionsLayout(QGridLayout):
    """Layout which is responsible for input of all additional parameters, like party buffs,
    or the assumed number of kills or hits taken."""

    def __init__(self, parent):
        super().__init__()

        self.hits_taken_input = QHBoxLayout()

        self.hits_taken_cb = Combobox(
            parent,
            items=["--Assume hits taken--", "every turn",
                   "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        self.tooltip = Tooltip(
            tooltip_text=("It is assumed that you get hit for 10 energy. "
                          "However, generated energy can range from 2 to 25 energy "
                          "depending on the enemy that hits you "
                          "or the number of hits the attack constitutes of."))

        self.kills_input = Combobox(
            parent,
            items=["--Assume kills--", "every turn",
                   "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])

        self.ult_kills_input = Combobox(
            parent,
            items=["--Assume Ult kills--", "1", "2", "3", "4", "5"])
        self.ult_kills_input.setEnabled(False)

        self.assume_ult = CheckBox(
            parent, "Assume Ultimate Activation",
            tooltip_text=("Assume Rotation starts with Ultimate activation. "
                          "They refund 5 energy on their activation."),
            checked=True)

        self.assume_tingyun_ult = CheckBox(
            parent, "Assume Tingyun Ult",
            tooltip_text="Tingyun Ultimate grants additional 50 energy.")

        self.assume_tingyun_e6 = CheckBox(
            parent, "Assume Tingyun E6",
            tooltip_text="Tingyun Eidolon 6 grants additional 10 energy on her Ultimate.")

        self.show_detailed_breakdown = CheckBox(
            parent, "Show detailed energy breakdown?",
            tooltip_text=("Currently limited, albeit accurate, energy breakdown "
                          "which lists energy sources and the amount of energy they generate."))

        self.enemy_weakness = CheckBox(
            parent, "Enemy has correctly weakness?",
            tooltip_text="Does the enemy has a weakness matching character's element?")

        self.hits_taken_input.addWidget(self.hits_taken_cb, stretch=1)
        self.hits_taken_input.addWidget(self.tooltip)
        self.addLayout(self.hits_taken_input, 7, 0)
        self.addWidget(self.kills_input, 7, 1)
        self.addWidget(self.ult_kills_input, 7, 2)
        self.addWidget(self.assume_ult, 8, 0)
        self.addWidget(self.assume_tingyun_ult, 8, 1)
        self.addWidget(self.assume_tingyun_e6, 8, 2)
        self.addWidget(self.show_detailed_breakdown, 9, 0)
        self.addWidget(self.enemy_weakness, 9, 1)


@dataclass
class ButtonLayout(QGridLayout):
    """Button layout with buttons for confirmation of all inputs,
    and button for refreshing the window, that is,
    for resetting all input value to their default values."""

    def __init__(self, parent):
        super().__init__()

        self.confirm_button = QPushButton("Confirm Selection")
        self.confirm_button.clicked.connect(parent._confirm_selection)
        self.confirm_button.setEnabled(False)

        self.reset_button = QPushButton("Reset Window")
        self.reset_button.clicked.connect(parent._refresh_window)
        padding_row = QWidget()
        self.addWidget(padding_row, 99, 0, 2, 2)
        self.addWidget(self.reset_button, 100, 0)
        self.addWidget(self.confirm_button, 100, 1)
