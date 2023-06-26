from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QLabel,
    QPushButton,
    QSpinBox,
)


def add_combobox(
    layout,
    label,
    items,
    row: int = 0,
    column: int = 0,
    label_stack=False,
    callback=None,
    width=150,
    tooltip=None,
):
    if label_stack:
        combobox_row = row + 1
        combobox_column = column
    else:
        combobox_row = row
        combobox_column = column + 1
    combobox = QComboBox()
    combobox.addItems(items)
    if callback:
        combobox.currentIndexChanged.connect(callback)
    combobox.setMaximumWidth = width

    if label is not None:
        combobox_label = QLabel(label)
        combobox_label.setMaximumWidth = width
        layout.addWidget(combobox_label, row, column)
    else:
        combobox_label = None

    if tooltip:
        combobox.setToolTip(tooltip)
    layout.addWidget(combobox, combobox_row, combobox_column)
    return combobox, combobox_label


def add_button(
    label,
    layout,
    connected_function,
    *,
    row: int = 0,
    column: int = 0,
    visibility=True,
    minimum_width=0,
    alignment="center",
    tooltip=None,
):
    button = QPushButton(label)
    if alignment == "center":
        pass
    elif alignment == "left":
        button.setStyleSheet("QPushButton { text-align: left; }")
    elif alignment == "right":
        button.setStyleSheet("QPushButton { text-align: right; }")

    button.setVisible(visibility)
    button.setMinimumWidth(minimum_width)

    if tooltip:
        button.setToolTip(tooltip)
    layout.addWidget(button, row, column)
    button.clicked.connect(connected_function)
    return button


def add_checkbox(
    layout, default, label, row: int = 0, column: int = 0, tooltip=None
):
    box = QCheckBox()
    box.setChecked(default)
    if tooltip:
        box.setToolTip(tooltip)
    layout.addWidget(QLabel(label), row, column)
    layout.addWidget(box, row, column + 1)
    return box


def add_float_box(
    layout,
    default,
    minimum,
    maximum,
    label,
    step,
    row: int = 0,
    column: int = 0,
    tooltip=None,
):
    box = QDoubleSpinBox()
    box.setMinimum(minimum)
    box.setMaximum(maximum)
    box.setValue(default)
    box.setSingleStep(step)
    if tooltip:
        box.setToolTip(tooltip)
    layout.addWidget(QLabel(label), row, column)
    layout.addWidget(box, row, column + 1)
    return box


def add_int_box(
    layout,
    default,
    minimum,
    maximum,
    label,
    row: int = 0,
    column: int = 0,
    tooltip=None,
):
    box = QSpinBox()
    box.setMinimum(minimum)
    box.setMaximum(maximum)
    # Not always set if not after min & max
    box.setValue(default)
    if tooltip:
        box.setToolTip(tooltip)
    layout.addWidget(QLabel(label), row, column)
    layout.addWidget(box, row, column + 1)
    return box
