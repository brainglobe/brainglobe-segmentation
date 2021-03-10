# RegionSeg
from qtpy.QtWidgets import (
    QGridLayout,
    QGroupBox,
)

from brainreg_segment.layout.utils import display_warning
from brainreg_segment.layout.gui_elements import (
    add_button,
    add_checkbox,
)

from brainreg_segment.regions.layers import (
    add_existing_region_segmentation,
    add_new_region_layer,
)

from brainreg_segment.regions.analysis import region_analysis
from brainreg_segment.layout.gui_constants import (
    COLUMN_WIDTH,
    SEGM_METHODS_PANEL_ALIGN,
    CALCULATE_VOLUMES_DEFAULT,
    SUMMARIZE_VOLUMES_DEFAULT,
    BRUSH_SIZE,
    IMAGE_FILE_EXT,
    NUM_COLORS,
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
        brush_size=BRUSH_SIZE,
        image_file_extension=IMAGE_FILE_EXT,
        num_colors=NUM_COLORS,
    ):

        super(RegionSeg, self).__init__()
        self.parent = parent

        self.calculate_volumes_default = calculate_volumes_default
        self.summarise_volumes_default = summarise_volumes_default

        # Brushes / ...
        self.brush_size_default = BRUSH_SIZE  # Keep track of default
        self.brush_size = brush_size  # Initialise
        self.num_colors = num_colors

        # File formats
        self.image_file_extension = image_file_extension

    def add_region_panel(self, row):
        self.region_panel = QGroupBox("Region analysis")
        region_layout = QGridLayout()

        add_button(
            "Add region",
            region_layout,
            self.add_region,
            2,
            0,
        )

        add_button(
            "Analyse regions",
            region_layout,
            self.run_region_analysis,
            2,
            1,
        )

        self.calculate_volumes_checkbox = add_checkbox(
            region_layout,
            self.calculate_volumes_default,
            "Calculate volumes",
            0,
        )

        self.summarise_volumes_checkbox = add_checkbox(
            region_layout,
            self.summarise_volumes_default,
            "Summarise volumes",
            1,
        )

        region_layout.setColumnMinimumWidth(1, COLUMN_WIDTH)
        self.region_panel.setLayout(region_layout)
        self.parent.layout.addWidget(self.region_panel, row, 0, 1, 2)
        self.region_panel.setVisible(False)

    def toggle_region_panel(self):
        # TODO: Change color scheme directly when theme is switched
        # TODO: "text-align" property should follow constant SEGM_METHODS_PANEL_ALIGN
        if self.region_panel.isVisible():
            self.region_panel.setVisible(False)
            if self.parent.viewer.theme == "dark":
                self.parent.show_regionseg_button.setStyleSheet(
                    f"QPushButton {{ background-color: #414851; text-align:{SEGM_METHODS_PANEL_ALIGN};}}"
                    f"QPushButton:pressed {{ background-color: #414851; text-align:{SEGM_METHODS_PANEL_ALIGN};}}"
                )
            else:
                self.parent.show_regionseg_button.setStyleSheet(
                    f"QPushButton {{ background-color: #d6d0ce; text-align:{SEGM_METHODS_PANEL_ALIGN};}}"
                    f"QPushButton:pressed {{ background-color: #d6d0ce; text-align:{SEGM_METHODS_PANEL_ALIGN};}}"
                )

        else:
            self.region_panel.setVisible(True)
            if self.parent.viewer.theme == "dark":
                self.parent.show_regionseg_button.setStyleSheet(
                    f"QPushButton {{ background-color: #7e868f; text-align:{SEGM_METHODS_PANEL_ALIGN};}}"
                    f"QPushButton:pressed {{ background-color: #7e868f; text-align:{SEGM_METHODS_PANEL_ALIGN};}}"
                )
            else:
                self.parent.show_regionseg_button.setStyleSheet(
                    f"QPushButton {{ background-color: #fdf194; text-align:{SEGM_METHODS_PANEL_ALIGN};}}"
                    f"QPushButton:pressed {{ background-color: #fdf194; text-align:{SEGM_METHODS_PANEL_ALIGN};}}"
                )

    def check_saved_region(self):
        add_existing_region_segmentation(
            self.parent.paths.regions_directory,
            self.parent.viewer,
            self.parent.label_layers,
            self.image_file_extension,
        )

    def add_region(self):
        print("Adding a new region\n")
        self.region_panel.setVisible(True)  # Should be visible by default!
        add_new_region_layer(
            self.parent.viewer,
            self.parent.label_layers,
            self.parent.base_layer.data,
            self.brush_size,
            self.num_colors,
        )

    def run_region_analysis(self):
        if self.parent.label_layers:
            choice = display_warning(
                self.parent,
                "About to analyse regions",
                "Existing files will be will be deleted. Proceed?",
            )
            if choice:
                print("Running region analysis")
                worker = region_analysis(
                    self.parent.label_layers,
                    self.parent.atlas_layer.data,
                    self.parent.atlas,
                    self.parent.hemispheres_data,
                    self.parent.paths.regions_directory,
                    output_csv_file=self.parent.paths.region_summary_csv,
                    volumes=self.calculate_volumes_checkbox.isChecked(),
                    summarise=self.summarise_volumes_checkbox.isChecked(),
                )
                worker.start()
            else:
                print("Preventing analysis as user chose 'Cancel'")
        else:
            print("No regions found")
