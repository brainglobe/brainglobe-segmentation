from brainglobe_utils.qtpy.dialog import display_info, display_warning
from brainglobe_utils.qtpy.interaction import add_button, add_checkbox
from qtpy.QtWidgets import QGridLayout, QGroupBox

from brainglobe_segmentation.layout.gui_constants import (
    BRUSH_SIZE,
    CALCULATE_VOLUMES_DEFAULT,
    COLUMN_WIDTH,
    IMAGE_FILE_EXT,
    SAVE_DEFAULT,
    SEGM_METHODS_PANEL_ALIGN,
    SUMMARIZE_VOLUMES_DEFAULT,
)
from brainglobe_segmentation.regions.analysis import region_analysis
from brainglobe_segmentation.regions.layers import (
    add_existing_region_segmentation,
    add_new_region_layer,
    add_region_from_existing_layer,
)


class RegionSeg(QGroupBox):
    """
    Region segmentation method panel

    """

    def __init__(
        self,
        parent,
        calculate_volumes_default=CALCULATE_VOLUMES_DEFAULT,
        summarise_volumes_default=SUMMARIZE_VOLUMES_DEFAULT,
        save_default=SAVE_DEFAULT,
        brush_size=BRUSH_SIZE,
        image_file_extension=IMAGE_FILE_EXT,
    ):
        super(RegionSeg, self).__init__()
        self.parent = parent

        self.calculate_volumes_default = calculate_volumes_default
        self.summarise_volumes_default = summarise_volumes_default
        self.save_default = save_default

        # Brushes / ...
        self.brush_size_default = BRUSH_SIZE  # Keep track of default
        self.brush_size = brush_size  # Initialise

        # File formats
        self.image_file_extension = image_file_extension

    def add_region_panel(self, row):
        self.region_panel = QGroupBox("Region analysis")
        region_layout = QGridLayout()

        add_button(
            "Add new region",
            region_layout,
            self.add_new_region,
            row=3,
            column=0,
            tooltip="Create a new empty segmentation layer "
            "to manually segment a new region.",
        )

        add_button(
            "Analyse regions",
            region_layout,
            self.run_region_analysis,
            row=3,
            column=1,
            tooltip="Analyse the spatial distribution of the "
            "segmented regions.",
        )
        add_button(
            "Add region from selected layer",
            region_layout,
            self.add_region_from_existing_layer,
            row=4,
            column=0,
            tooltip="Adds a region from a selected labels layer (e.g. "
            "from another plugin). Make sure this region "
            "was segmented from the currently loaded "
            "brainreg result (i.e. atlas/sample space)!",
        )

        self.calculate_volumes_checkbox = add_checkbox(
            region_layout,
            self.calculate_volumes_default,
            "Calculate volumes",
            row=0,
            tooltip="Calculate and save the volume of each "
            "brain region included in the segmented "
            "region.",
        )

        self.summarise_volumes_checkbox = add_checkbox(
            region_layout,
            self.summarise_volumes_default,
            "Summarise volumes",
            row=1,
            tooltip="Summarise each segmented region "
            "(e.g. center, volume etc.).",
        )
        self.save_checkbox = add_checkbox(
            region_layout,
            self.save_default,
            "Save segmentation",
            row=2,
            tooltip="Save the segmentation layers during analysis.",
        )

        region_layout.setColumnMinimumWidth(1, COLUMN_WIDTH)
        self.region_panel.setLayout(region_layout)
        self.parent.layout.addWidget(self.region_panel, row, 0, 1, 2)
        self.region_panel.setVisible(False)

    def toggle_region_panel(self):
        if self.region_panel.isVisible():
            self.region_panel.setVisible(False)
            if self.parent.viewer.theme == "dark":
                self.parent.show_regionseg_button.setStyleSheet(
                    f"QPushButton {{ background-color: #414851; text-align:"
                    f"{SEGM_METHODS_PANEL_ALIGN};}}"
                    f"QPushButton:pressed {{ background-color: #414851; "
                    f"text-align:{SEGM_METHODS_PANEL_ALIGN};}}"
                )
            else:
                self.parent.show_regionseg_button.setStyleSheet(
                    f"QPushButton {{ background-color: #d6d0ce; text-align:"
                    f"{SEGM_METHODS_PANEL_ALIGN};}}"
                    f"QPushButton:pressed {{ background-color: #d6d0ce; "
                    f"text-align:{SEGM_METHODS_PANEL_ALIGN};}}"
                )

        else:
            self.region_panel.setVisible(True)
            if self.parent.viewer.theme == "dark":
                self.parent.show_regionseg_button.setStyleSheet(
                    f"QPushButton {{ background-color: #7e868f; text-align:"
                    f"{SEGM_METHODS_PANEL_ALIGN};}}"
                    f"QPushButton:pressed {{ background-color: #7e868f; "
                    f"text-align:{SEGM_METHODS_PANEL_ALIGN};}}"
                )
            else:
                self.parent.show_regionseg_button.setStyleSheet(
                    f"QPushButton {{ background-color: #fdf194; text-align:"
                    f"{SEGM_METHODS_PANEL_ALIGN};}}"
                    f"QPushButton:pressed {{ background-color: #fdf194; "
                    f"text-align:{SEGM_METHODS_PANEL_ALIGN};}}"
                )

    def check_saved_region(self):
        add_existing_region_segmentation(
            self.parent.paths.regions_directory,
            self.parent.viewer,
            self.parent.label_layers,
            self.image_file_extension,
        )

    def add_new_region(self):
        print("Adding a new region\n")
        self.region_panel.setVisible(True)  # Should be visible by default!
        add_new_region_layer(
            self.parent.viewer,
            self.parent.label_layers,
            self.parent.base_layer.data,
            self.brush_size,
        )

    def add_region_from_existing_layer(self, override=False):
        print("Adding region from existing layer\n")
        selected_layer = self.parent.viewer.layers.selection.active
        try:
            add_region_from_existing_layer(
                selected_layer, self.parent.label_layers
            )
            if not override:
                display_info(
                    self.parent,
                    "Layer added",
                    f"Added layer: {str(selected_layer)}.",
                )
        except TypeError:
            if not override:
                display_info(
                    self.parent,
                    "Unsupported layer type",
                    "Selected layer is not a label layer. "
                    "Please select a label layer and try again.",
                )

    def run_region_analysis(self, override=False):
        if self.parent.label_layers:
            if not override:
                choice = display_warning(
                    self.parent,
                    "About to analyse regions",
                    "Please ensure the regions were segmented in the same "
                    "reference space as the currently open image. "
                    "Existing files will be will be deleted. Proceed?",
                )
            else:
                choice = True  # for debugging

            if choice:
                if self.save_checkbox.isChecked():
                    self.parent.run_save()

                print("Running region analysis")

                if check_segmentation_in_correct_space(
                    self.parent.label_layers,
                    self.parent.annotations_layer.data,
                ):
                    worker = region_analysis(
                        self.parent.label_layers,
                        self.parent.annotations_layer.data,
                        self.parent.atlas,
                        self.parent.hemispheres_data,
                        self.parent.paths.regions_directory,
                        output_csv_file=self.parent.paths.region_summary_csv,
                        volumes=self.calculate_volumes_checkbox.isChecked(),
                        summarise=self.summarise_volumes_checkbox.isChecked(),
                    )
                    worker.start()
                else:
                    display_incorrect_space_warning(self.parent)
                    return
            else:
                print("Preventing analysis as user chose 'Cancel'")
        else:
            print("No regions found")


def check_segmentation_in_correct_space(label_layers, annotations_layer_image):
    for label_layer in label_layers:
        if label_layer.data.shape != annotations_layer_image.shape:
            return False
    return True


def display_incorrect_space_warning(widget):
    display_info(
        widget,
        "Incorrect coordinate space",
        "One or more of the segmented images are not of the same size "
        "as the registered image. Please ensure you segmented your "
        "data in the same coordinate space as you wish to analyse it in. ",
    )
