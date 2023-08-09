"""GUI that allows the user to input various parameters:
    - character
    - character related parameters (like Eidolons, certain talents, and abilities)
    - equipment (like Light Cones, Relics, Ornaments, Ropes)
    - team buffs (e.g., Tingyun Ultimate)
    - additional parameters like the number of kills and hits taken."""

from dataclasses import dataclass
from typing import Literal, Optional
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QWidget,
                             QComboBox, QPushButton, QGridLayout,
                             QCheckBox, QLabel, QFormLayout, QStyle)
from PyQt6.QtCore import Qt
from gui_utils import UserInput, get_int_from_selector, get_int_or_literal_from_selector
from characters import CharStats, CHARACTERS, SUPPORTED_CHARACTERS
from eidolons import EIDOLONS
from talents import TALENTS
from abilities import ABILITIES
from follow_ups import FOLLOW_UP_ATTACKS
from light_cones import LIGHT_CONES, LIGHT_CONE_NAMES
from relics import Relic, ALL_RELICS, RELICS, ORNAMENTS, ROPES
from calculations import run_calculations


@dataclass
class MainWindowDemo(QDialog):
    """Main GUI window which allows the user to input all parameters."""

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(350)
        self.setWindowTitle("HSR Rotation Calculator Demo")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self._setup_layout()

    def _setup_layout(self) -> None:
        """Creates and sets layout which allows user to input all the parameters."""

        layout = QVBoxLayout()
        self.char_layout = CharSelectorLayout(self)
        self.grid_layout = QGridLayout()
        self.grid_layout.addLayout(self.char_layout, 0, 0)
        layout.addLayout(self.grid_layout)

        self.lc_layout = LightConeSelectionLayout(self)
        layout.addLayout(self.lc_layout)

        self.relic_layout = RelicSelectionLayout(self)
        layout.addLayout(self.relic_layout)

        self.options_layout = OptionsLayout(self)
        layout.addLayout(self.options_layout)

        self.button_layout = ButtonLayout(self)
        layout.addLayout(self.button_layout)
        self.setLayout(layout)

    def _get_compatible_lc(self) -> None:
        """Filters out Light Cones that are not compatible with the character's path
        as they provide no relevant bonuses. Then adds these LCs to the relevant combobox.

        If there are no compatible LCs placeholder text will be displayed instead,
        and the combobox will be disabled."""

        selected_character = self.char_layout.char_selector.currentText()
        char = CHARACTERS[selected_character]
        char_path = char.path
        lcs = [lc.name for lc in LIGHT_CONES.values() if lc.path == char_path]
        self.lc_layout.lc_selector.clear()

        if lcs:
            self.lc_layout.lc_selector.setEnabled(True)
            self.lc_layout.lc_selector.addItems(
                ["--Select Light Cone--"] + lcs)
            self.lc_layout.lc_selector.clearEditText()
            self.lc_layout.lc_selector.setPlaceholderText(
                "--Select Light Cone--")
        else:
            self.lc_layout.lc_selector.setPlaceholderText(
                "No supported Light Cones for this Path")
            self.lc_layout.lc_selector.setEnabled(False)

    def _refresh_window(self) -> None:
        """Quick and dirty way of refreshing the window."""

        self.close()
        dialog = MainWindowDemo()
        dialog.exec()

    def _enable_confirm_button(self) -> None:
        self.button_layout.confirm_button.setEnabled(True)

    def _confirm_selection(self) -> None:
        """Gathers all user input parameters then runs all necessary calculations."""

        user_input = self._gather_user_input()
        char = CHARACTERS.get(user_input.char_name)
        if not char:
            return

        stats = CharStats(char.ult_cost)
        if char.is_skill_attack:
            stats.is_skill_attack = True
        if char.is_ult_attack:
            stats.is_skill_attack = True

        run_calculations(stats, user_input)

    def _gather_user_input(self) -> UserInput:
        """Gathers user input and stores it to a UserInput object,
        then returns said object."""

        char_name = self.char_layout.char_selector.currentText()
        eidolons = self._get_eidolons()
        technique = self.char_layout.technique_check.checkbox.isChecked()
        talent_level = self._get_talent_level()
        ability = self.char_layout.ability_selector.currentText()

        light_cone = self.lc_layout.lc_selector.currentText()
        superimposition = self.lc_layout.si_selector.currentIndex()
        relic = self._get_relic()
        num_relic_trigger = self._get_relic_trigger()
        ornament = self.relic_layout.ornament_selector.currentText()
        rope = self.relic_layout.rope_selector.currentText()

        num_hits_taken = self._get_hits_taken()
        num_follow_ups = self._get_num_follow_ups()
        num_kills = self._get_kills()
        num_ult_kills = self._get_ult_kills()
        assume_ult = self.options_layout.assume_ult.checkbox.isChecked()
        assume_tingyun_ult = self.options_layout.assume_tingyun_ult.checkbox.isChecked()
        assume_tingyun_e6 = self.options_layout.assume_tingyun_e6.checkbox.isChecked()
        detailed_breakdown = self.options_layout.show_detailed_breakdown.checkbox.isChecked()
        matching_enemy_weakness = self.options_layout.enemy_weakness.checkbox.isChecked()

        return UserInput(char_name, eidolons, talent_level, ability,
                         light_cone, superimposition, relic,
                         num_relic_trigger, ornament, rope,
                         num_hits_taken, num_follow_ups, num_kills, num_ult_kills,
                         assume_ult, assume_tingyun_ult, assume_tingyun_e6,
                         technique, detailed_breakdown, matching_enemy_weakness)

    def _get_eidolons(self) -> int:
        """Returns the selected number of eidolons."""
        return get_int_from_selector(self.char_layout.eidolons_selector)

    def _get_talent_level(self) -> int:
        """Returns the selected talent level."""
        return get_int_from_selector(self.char_layout.talent_selector)

    def _get_relic(self) -> Optional[Relic]:
        """Returns the selected relic object."""
        relic_name = self.relic_layout.relic_selector.currentText()
        return ALL_RELICS.get(relic_name)

    def _get_relic_trigger(self) -> int | Literal["every turn"]:
        """Returns the selected number of relic triggers."""
        return get_int_or_literal_from_selector(self.relic_layout.relic_trigger_input)

    def _get_hits_taken(self) -> int | Literal["every turn"]:
        """Returns the selected number of hits taken."""
        return get_int_or_literal_from_selector(self.options_layout.hits_taken_input)

    def _get_num_follow_ups(self) -> int | Literal["every turn"]:
        """Returns the selected number of follow-up attacks."""
        return get_int_or_literal_from_selector(self.char_layout.follow_up_selector)

    def _get_kills(self) -> int | Literal["every turn"]:
        """Returns the selected number of kills."""
        return get_int_or_literal_from_selector(self.options_layout.kills_input)

    def _get_ult_kills(self) -> int:
        """Returns the selected number of ult kills."""
        return get_int_from_selector(self.options_layout.ult_kills_input)


@dataclass
class CharSelectorLayout(QGridLayout):
    """Layout which is responsible for input of all parameters related to characters,
    i.e., their name, Eidolons, talents, abilities, and follow-up attacks."""

    def __init__(self, parent: MainWindowDemo):
        super().__init__()

        self.char_selector = _CustomCombobox(
            parent, "--Select Character--", SUPPORTED_CHARACTERS)
        self.char_selector.setMinimumWidth(250)
        self.char_selector.currentTextChanged.connect(
            parent._get_compatible_lc)
        self.char_selector.currentTextChanged.connect(self._enable_options)
        self.char_selector.currentTextChanged.connect(
            parent._enable_confirm_button)

        self.eidolons_selector = _CustomCombobox(
            parent, items=["--Eidolon Level--"])
        self.eidolons_selector.setEnabled(False)

        self.ability_selector = _CustomCombobox(
            parent, items=["--Character Ability--"])
        self.ability_selector.setEnabled(False)

        self.talent_selector = _CustomCombobox(
            parent, items=["--Talent Level--"] + [f"{i}" for i in range(1, 16)])
        self.talent_selector.setEnabled(False)

        self.follow_up_selector = _CustomCombobox(
            parent, items=["--Follow-up Attacks--", "every turn",
                           "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        self.follow_up_selector.setEnabled(False)

        self.technique_check = _CustomCheckBox(
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

    def _enable_options(self) -> None:
        char_name = self.char_selector.currentText()

        self.eidolons_selector.setEnabled(True)
        char_ability = (["--Character Ability--"] + [a.name for a in ABILITIES.values()
                                                     if a.char_name == char_name])
        if len(char_ability) > 1:
            self.ability_selector.setEnabled(True)
            self.ability_selector.clear()
            self.ability_selector.addItems(char_ability)

        else:
            self.ability_selector.setEnabled(False)
            self.ability_selector.setPlaceholderText("--Character Ability--")

        char_eidolons = [str(e.eidolon_level) for e in EIDOLONS
                         if e.char_name == char_name]
        if char_eidolons:
            self.eidolons_selector.setEnabled(True)
            self.eidolons_selector.clear()
            self.eidolons_selector.addItems(
                ["--Eidolon Level--"] + char_eidolons)
        else:
            self.eidolons_selector.setEnabled(False)

        if TALENTS.get(char_name):
            self.talent_selector.setEnabled(True)
        else:
            self.talent_selector.setEnabled(False)

        # Blade's follow-ups are already included in his rotations
        if FOLLOW_UP_ATTACKS.get(char_name) and char_name != "Blade":
            self.follow_up_selector.setEnabled(True)
        else:
            self.follow_up_selector.setEnabled(False)

        if char_name in ("Blade", "Luka"):
            self.technique_check.setEnabled(True)
        else:
            self.technique_check.setEnabled(False)


@dataclass
class LightConeSelectionLayout(QGridLayout):
    """Layout which is responsible for input of all parameters related to Light Cones,
    i.e., their name, and their superimposition rank."""

    def __init__(self, parent: MainWindowDemo):
        super().__init__()

        self.lc_selector = _CustomCombobox(
            parent, items=["--Select Light Cone--"] + LIGHT_CONE_NAMES)
        self.lc_selector.setMinimumWidth(250)
        self.lc_selector.currentTextChanged.connect(self._set_default_si)
        self.lc_selector.currentTextChanged.connect(
            self._enable_superimposition)

        self.si_selector = _CustomCombobox(parent, "--Superimposition Level--",
                                           ["Superimposition 1", "Superimposition 2",
                                            "Superimposition 3", "Superimposition 4",
                                            "Superimposition 5"])
        self.si_selector.setEnabled(False)

        self.addWidget(self.lc_selector, 3, 0)
        self.addWidget(self.si_selector, 3, 1)

    def _enable_superimposition(self) -> None:
        self.si_selector.setEnabled(True)

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
class RelicSelectionLayout(QGridLayout):
    """Layout which is responsible for input of all parameters related to all types of relics,
    i.e., regular relics, ornaments, and energy recharge ropes.
    Additionally, user can configure how many times relic effects are triggered."""

    def __init__(self, parent: MainWindowDemo):
        super().__init__()

        self.relic_selector = _CustomCombobox(
            parent, "--Select Relic--", RELICS)
        self.relic_selector.currentTextChanged.connect(
            self._enable_relic_toggle)
        self.relic_trigger_input = _CustomCombobox(
            parent,
            items=["--Relic triggers--", "every turn",
                   "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        self.relic_trigger_input.setEnabled(False)
        self.relic_selector.setMinimumWidth(250)

        self.ornament_selector = _CustomCombobox(
            parent, items=["--Select Ornament--"] + ORNAMENTS)

        self.rope_selector = _CustomCombobox(
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

    def __init__(self, parent: MainWindowDemo):
        super().__init__()

        self.hits_taken_input = _CustomCombobox(
            parent,
            items=["--Assume hits taken--", "every turn",
                   "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])

        self.kills_input = _CustomCombobox(
            parent,
            items=["--Assume kills--", "every turn",
                   "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])

        self.ult_kills_input = _CustomCombobox(
            parent,
            items=["--Assume Ult kills--", "1", "2", "3", "4", "5"])

        self.assume_ult = _CustomCheckBox(
            parent, "Assume Ultimate Activation",
            tooltip_text=("Assume Rotation starts with Ultimate activation. "
                          "They refund 5 energy on their activation."),
            checked=True)

        self.assume_tingyun_ult = _CustomCheckBox(
            parent, "Assume Tingyun Ult",
            tooltip_text="Tingyun Ultimate grants additional 50 energy.")

        self.assume_tingyun_e6 = _CustomCheckBox(
            parent, "Assume Tingyun E6",
            tooltip_text="Tingyun Eidolon 6 grants additional 10 energy on her Ultimate.")

        self.show_detailed_breakdown = _CustomCheckBox(
            parent, "Show detailed energy breakdown?",
            tooltip_text=("Currently limited, albeit accurate, energy breakdown "
                          "which lists energy sources and the amount of energy they generate."))

        self.enemy_weakness = _CustomCheckBox(
            parent, "Enemy has correctly weakness?",
            tooltip_text="Does the enemy has a weakness matching character's element?")

        self.addWidget(self.hits_taken_input, 7, 0)
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

    def __init__(self, parent: MainWindowDemo):
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


@dataclass
class _CustomCombobox(QComboBox):
    def __init__(self, parent, text="", items: Optional[list[str]] = None):
        super().__init__(parent)
        self.setPlaceholderText(text)
        if items:
            self.addItems(items)
        self.setMaxVisibleItems(20)
        self.clearEditText()


@dataclass
class _CustomCheckBox(QWidget):
    """A custom widget for displaying a checkbox with tooltip."""

    def __init__(self, parent: QWidget, label: str,
                 tooltip_text: str, checked=False) -> None:
        super().__init__(parent)

        form_layout = QFormLayout()
        self.checkbox = QCheckBox(label)
        self.checkbox.setChecked(checked)
        self.tooltip = QLabel()
        self.icon = QStyle.StandardPixmap.SP_MessageBoxQuestion
        self.tooltip.setPixmap(parent.style().standardPixmap(self.icon))
        self.tooltip.setToolTip(tooltip_text)
        form_layout.addRow(self.checkbox, self.tooltip)
        self.setLayout(form_layout)
