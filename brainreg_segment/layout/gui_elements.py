# GUI ELEMENTS
# from napari.resources import build_icons # Contains .SVGPATH to all icons for napari

from qtpy.QtWidgets import (
    QDoubleSpinBox,
    QPushButton,
    QCheckBox,
    QLabel,
    QSpinBox,
    QComboBox,
)


def add_combobox(
    layout,
    label,
    items,
    row,
    column=0,
    label_stack=False,
    callback=None,
    width=150,
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

    layout.addWidget(combobox, combobox_row, combobox_column)
    return combobox, combobox_label


def add_button(
    label,
    layout,
    connected_function,
    row,
    column,
    visibility=True,
    minimum_width=0,
    alignment="center",
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
    layout.addWidget(button, row, column)
    button.clicked.connect(connected_function)
    return button


# def add_radiobutton(
#     label,
#     layout,
#     connected_function,
#     row,
#     column,
#     visibility=True,
#     minimum_width=0,
#     alignment="center",
# ):
#     button = QRadioButton(label)
#     if alignment == "center":
#         pass
#     elif alignment == "left":
#         button.setStyleSheet(
#             "QRadioButton { text-align: left; padding: 0; spacing: 30px;}"
#         )
#     elif alignment == "right":
#         button.setStyleSheet(
#             "QRadioButton { text-align: right; padding: 0; spacing: 30px;}"
#         )

#     # Too change indicator button ... needs to dynamically retrieve icon from Napari.
#     # Icons are saved as .svg files under napari.resources SVGPATH
#     # "QRadioButton::indicator"
#     # "{"
#     # "width:16px;"
#     # "height:16px;"
#     # "}"
#     # "QRadioButton::indicator::unchecked"
#     # "{"
#     # "image: url(build_icons.SVGPATH/visibility_off.svg);"
#     # "}"
#     # "QRadioButton::indicator::checked"
#     # "{"
#     # "image: url(/opt/miniconda3/envs/analysis/lib/python3.6/site-packages/napari/resources/icons/visibility.svg);"
#     # "}"
#     # )

#     button.setVisible(visibility)
#     button.setMinimumWidth(minimum_width)
#     layout.addWidget(button, row, column)
#     button.clicked.connect(connected_function)
#     return button


def add_checkbox(layout, default, label, row, column=0):
    box = QCheckBox()
    box.setChecked(default)
    layout.addWidget(QLabel(label), row, column)
    layout.addWidget(box, row, column + 1)
    return box


def add_float_box(
    layout, default, minimum, maximum, label, step, row, column=0
):
    box = QDoubleSpinBox()
    box.setMinimum(minimum)
    box.setMaximum(maximum)
    box.setValue(default)
    box.setSingleStep(step)
    layout.addWidget(QLabel(label), row, column)
    layout.addWidget(box, row, column + 1)
    return box


def add_int_box(layout, default, minimum, maximum, label, row, column=0):
    box = QSpinBox()
    box.setMinimum(minimum)
    box.setMaximum(maximum)
    # Not always set if not after min & max
    box.setValue(default)
    layout.addWidget(QLabel(label), row, column)
    layout.addWidget(box, row, column + 1)
    return box
