"""GUI that allows the user to input various parameters:
    - character
    - character related parameters (like Eidolons, certain talents, and abilities)
    - equipment (like Light Cones, Relics, Ornaments, Ropes)
    - team buffs (e.g., Tingyun Ultimate)
    - additional parameters like the number of kills and hits taken."""

from dataclasses import dataclass
from typing import Literal, Optional
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from .widgets import (CharSelectorLayout, LightConeSelectionLayout,
                      SupportLightConeSelectionLayout, RelicSelectionLayout,
                      OptionsLayout, ButtonLayout)
from .gui_utils import UserInput
from .gui_utils import get_int_from_selector, get_int_or_literal_from_selector
from characters import CharStats, CHARACTERS
from light_cones import LIGHT_CONES
from relics import Relic, ALL_RELICS
from calculation_scripts.calculations import run_calculations


@dataclass
class MainWindowDemo(QDialog):
    """Main GUI window which allows the user to input all parameters."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("HSR Rotation Calculator Demo")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self._setup_layout()

    def _setup_layout(self) -> None:
        """Creates and sets layout which allows user to input all the parameters."""

        layout = QVBoxLayout()

        layout.addWidget(QLabel(text="Character info:"))
        self.char_layout = CharSelectorLayout(self)
        layout.addLayout(self.char_layout)

        layout.addWidget(QLabel(text="Equipment info:"))
        self.lc_layout = LightConeSelectionLayout(self)
        layout.addLayout(self.lc_layout)

        self.support_lc_layout = SupportLightConeSelectionLayout(self)
        layout.addLayout(self.support_lc_layout)

        self.relic_layout = RelicSelectionLayout(self)
        layout.addLayout(self.relic_layout)

        layout.addWidget(QLabel(text="Combat info:"))
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
        char = CHARACTERS.get(selected_character)
        if not char:
            return
        lcs = [lc.name for lc in LIGHT_CONES.values()
               if lc.path == char.path and not lc.is_support_lc]
        self.lc_layout.lc_selector.clear()

        if lcs:
            self.lc_layout.lc_selector.setEnabled(True)
            self.lc_layout.lc_selector.addItems(
                ["--Select Light Cone--"] + lcs)
            self.lc_layout.lc_selector.setPlaceholderText(
                "--Select Light Cone--")
        else:
            self.lc_layout.lc_selector.setPlaceholderText(
                "No supported Light Cones for this Path")
            self.lc_layout.lc_selector.setEnabled(False)
            self.lc_layout.si_selector.setEnabled(False)

    def _refresh_window(self) -> None:
        """Quick and dirty way of refreshing the window."""

        self.close()
        dialog = MainWindowDemo()
        dialog.exec()

    def _enable_confirm_button(self) -> None:
        self.button_layout.confirm_button.setEnabled(True)

    def _confirm_selection(self) -> None:
        """Confirms all input parameters then runs all necessary calculations."""

        self._collect_user_input()
        char = CHARACTERS.get(self.user_input.char_name)
        if not char:
            return

        stats = CharStats(char.ult_cost)
        if char.is_skill_attack:
            stats.is_skill_attack = True
        if char.is_ult_attack:
            stats.is_ult_attack = True

        run_calculations(stats, self.user_input)

    def _collect_user_input(self) -> None:
        """Collects user input and stores it to a UserInput object."""

        self.user_input = UserInput()
        self._collect_char_input()
        self._collect_gear_input()
        self._collect_combat_input()
        self._collect_other_input()
        self.user_input.cache("before-calculation")

    def _collect_char_input(self) -> None:
        """Collects character input, this includes:
        their name, their Eidolon level, talent level, ability possessed,
        as well as whether their technique was used before combat."""

        self.user_input.char_name = self.char_layout.char_selector.currentText()
        self.user_input.eidolons = self._get_eidolons()
        self.user_input.talent_level = self._get_talent_level()
        self.user_input.ability = self.char_layout.ability_selector.currentText()
        self.user_input.technique = self.char_layout.technique_check.checkbox.isChecked()

    def _collect_gear_input(self) -> None:
        """Collects gear input, this includes:
        Light Cone's name, its Superimposition level,
        equipped relic, and the number of its triggers,
        equipped ornament, and Energy Recharge rope."""

        self.user_input.light_cone = self._get_light_cone()
        self.user_input.support_light_cone = self._get_support_light_cone()
        if self.user_input.support_light_cone:
            self.user_input.support_light_cone.num_triggers = self._get_support_lc_triggers()

        self.user_input.relic = self._get_relic()
        self.user_input.num_relic_trigger = self._get_relic_trigger()
        self.user_input.ornament = self.relic_layout.ornament_selector.currentText()
        self.user_input.rope = self.relic_layout.rope_selector.currentText()

    def _collect_combat_input(self) -> None:
        """Collects combat input, this includes the number of the following:
        hits taken, kills, ultimate kills, and follow-up attacks."""

        self.user_input.num_hits_taken = self._get_hits_taken()
        self.user_input.ally_num_hits_taken = self._get_ally_hits_taken()
        self.user_input.num_kills = self._get_kills()
        self.user_input.num_ult_kills = self._get_ult_kills()
        self.user_input.num_follow_ups = self._get_num_follow_ups()

    def _collect_other_input(self) -> None:
        options = self.options_layout.check_boxes
        self.user_input.assume_ult = options.assume_ult.checkbox.isChecked()
        self.user_input.assume_tingyun_ult = options.assume_tingyun_ult.checkbox.isChecked()
        self.user_input.assume_tingyun_e6 = options.assume_tingyun_e6.checkbox.isChecked()
        self.user_input.detailed_breakdown = options.show_detailed_breakdown.checkbox.isChecked()
        self.user_input.matching_enemy_weakness = options.enemy_weakness.checkbox.isChecked()

    def _get_light_cone(self):
        light_cone_name = self.lc_layout.lc_selector.currentText()
        light_cone = LIGHT_CONES.get(light_cone_name)
        if light_cone:
            light_cone.superimposition = self.lc_layout.si_selector.currentIndex()
            return light_cone

        return None

    def _get_support_light_cone(self):
        support_light_cone_name = self.support_lc_layout.lc_selector.currentText()
        support_light_cone = LIGHT_CONES.get(support_light_cone_name)
        if support_light_cone:
            support_light_cone.superimposition = self.support_lc_layout.si_selector.currentIndex()
            return support_light_cone

        return None

    def _get_eidolons(self) -> int:
        """Returns the selected number of eidolons."""
        return get_int_from_selector(self.char_layout.eidolons_selector)

    def _get_talent_level(self) -> int:
        """Returns the selected talent level."""
        return get_int_from_selector(self.char_layout.talent_selector)

    def _get_support_lc_triggers(self) -> int | Literal["every turn"]:
        """Returns the selected number of relic triggers."""
        return get_int_or_literal_from_selector(self.support_lc_layout.trigger_input)

    def _get_relic(self) -> Optional[Relic]:
        """Returns the selected relic object."""
        relic_name = self.relic_layout.relic_selector.currentText()
        return ALL_RELICS.get(relic_name)

    def _get_relic_trigger(self) -> int | Literal["every turn"]:
        """Returns the selected number of relic triggers."""
        return get_int_or_literal_from_selector(self.relic_layout.relic_trigger_input)

    def _get_hits_taken(self) -> int | Literal["every turn"]:
        """Returns the selected number of hits taken."""
        return get_int_or_literal_from_selector(self.options_layout.combo_boxes.hits_taken_cb)

    def _get_ally_hits_taken(self) -> int | Literal["every turn"]:
        """Returns the selected number of hits taken."""
        return get_int_or_literal_from_selector(self.options_layout.combo_boxes.ally_hits_taken_cb)

    def _get_num_follow_ups(self) -> int | Literal["every turn"]:
        """Returns the selected number of follow-up attacks."""
        return get_int_or_literal_from_selector(self.char_layout.follow_up_selector)

    def _get_kills(self) -> int | Literal["every turn"]:
        """Returns the selected number of kills."""
        return get_int_or_literal_from_selector(self.options_layout.combo_boxes.kills_input)

    def _get_ult_kills(self) -> int:
        """Returns the selected number of ult kills."""
        return get_int_from_selector(self.options_layout.combo_boxes.ult_kills_input)
