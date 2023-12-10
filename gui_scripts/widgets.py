from dataclasses import dataclass
from typing import Optional, Iterable
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (QWidget, QLabel, QComboBox, QHBoxLayout,
                             QCheckBox, QFormLayout, QStyle, QSpinBox, QCompleter)


@dataclass
class Combobox(QComboBox):
    """Custom combobox widget.

    Attributes:
        - text (str): the first item and the placeholder text.
        - items (Iterable[str]) Optional: Items to be added to the combobox."""

    def __init__(self, parent=None, text=None, items: Optional[Iterable[str]] = None):
        super().__init__()
        self.text = text
        if self.text:
            self.addItem(self.text)
            self.setPlaceholderText(self.text)
        if items:
            self.addItems(items)
        self.setMaxVisibleItems(20)
        self.clearEditText()
        self.setDuplicatesEnabled(False)

    def reset_selection(self):
        """Resets widget to its default value."""

        all_items = [self.itemText(i) for i in range(self.count())]

        if self.text not in all_items:
            self.insertItem(0, self.text)

        self.setCurrentText(self.text)


@dataclass
class Tooltip(QLabel):
    """Custom tooltip widget."""

    def __init__(self, parent=None, text="", icon_size=QSize(16, 16)):
        super().__init__(parent)

        self.setToolTip(text)
        pixmap_name = QStyle.StandardPixmap.SP_MessageBoxQuestion

        style = self.style()
        if not style:
            return

        pixmap = style.standardPixmap(pixmap_name)
        resized_pixmap = pixmap.scaled(icon_size,
                                       Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(resized_pixmap)


@dataclass
class TooltipCheckBox(QWidget):
    """Custom widget for displaying a checkbox with tooltip."""

    def __init__(self, parent=None, label="", tooltip_text="",
                 checked=False, icon_size=QSize(16, 16)):
        super().__init__(parent)

        self.checked = checked
        form_layout = QFormLayout()
        self.checkbox = QCheckBox(label)
        self.checkbox.setChecked(checked)
        self.tooltip = Tooltip(parent, tooltip_text, icon_size)

        form_layout.addRow(self.checkbox, self.tooltip)
        form_layout.setContentsMargins(form_layout.contentsMargins().left(), 0,
                                       form_layout.contentsMargins().right(), 0)
        self.setLayout(form_layout)

    def reset_selection(self):
        """Resets widget to its default value."""
        self.checkbox.setChecked(self.checked)


class CounterInput(QWidget):
    def __init__(self, label_text, parent=None, show_checkbox=True, min=0, max=10):
        super().__init__(parent)
        self.max = max
        self.min = min
        self.show_checkbox = show_checkbox

        self.label = QLabel(label_text, self)
        self.label.setMaximumWidth(130)

        self.spin_box = QSpinBox(self)
        self.spin_box.setMaximum(self.max)
        self.spin_box.setMinimum(self.min)
        self.spin_box.setFixedWidth(50)

        self.check_box = None

        self.setup_layout()

    def setup_layout(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(layout.contentsMargins().left(), 0,
                                  layout.contentsMargins().right(), 0)
        layout.addWidget(self.label)
        layout.addWidget(self.spin_box)

        if self.show_checkbox:
            self.check_box = QCheckBox("Every Turn?", self)
            self.check_box.setMaximumWidth(100)
            layout.addWidget(self.check_box)
        else:
            invisible_widget = QWidget()
            invisible_widget.setMaximumWidth(100)
            layout.addWidget(invisible_widget)

    def get_num_input(self) -> int:
        """Returns the number input."""
        return self.spin_box.value()

    def repeats_every_turn(self) -> bool:
        """Returns whether or not the checkbox is checked,
        that is whether or not this input is applied very turn."""
        if self.check_box:
            return self.check_box.isChecked()

        return False

    def reset_selection(self):
        """Resets widget to its default value."""
        self.spin_box.setValue(self.min)
        if self.check_box:
            self.check_box.setChecked(False)


class SearchBox(Combobox):
    def __init__(self, text, parent=None, items: Iterable = []):
        super().__init__(parent, text, items)
        self.text = text
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if self.currentText() == self.text:
            self.setEditText("")

    def reset_selection(self):
        """Resets widget to its default value."""
        self.setEditText(self.text)
