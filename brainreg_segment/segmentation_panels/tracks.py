# TrackSeg
from glob import glob

import numpy as np
from qtpy.QtWidgets import QGridLayout, QGroupBox

from brainreg_segment.image.utils import create_KDTree_from_image
from brainreg_segment.layout.gui_constants import (
    COLUMN_WIDTH,
    FIT_DEGREE_DEFAULT,
    POINT_SIZE,
    SAVE_DEFAULT,
    SEGM_METHODS_PANEL_ALIGN,
    SPLINE_POINTS_DEFAULT,
    SPLINE_SIZE,
    SPLINE_SMOOTHING_DEFAULT,
    SUMMARISE_TRACK_DEFAULT,
    TRACK_FILE_EXT,
)
from brainreg_segment.layout.gui_elements import (
    add_button,
    add_checkbox,
    add_float_box,
    add_int_box,
)
from brainreg_segment.layout.utils import display_info, display_warning
from brainreg_segment.tracks.analysis import track_analysis
from brainreg_segment.tracks.layers import (
    add_existing_track_layers,
    add_new_track_layer,
    add_track_from_existing_layer,
)


class TrackSeg(QGroupBox):
    """
    Track segmentation method panel

    """

    def __init__(
        self,
        parent,
        point_size=POINT_SIZE,
        spline_size=SPLINE_SIZE,
        track_file_extension=TRACK_FILE_EXT,
        spline_points_default=SPLINE_POINTS_DEFAULT,
        spline_smoothing_default=SPLINE_SMOOTHING_DEFAULT,
        fit_degree_default=FIT_DEGREE_DEFAULT,
        summarise_track_default=SUMMARISE_TRACK_DEFAULT,
        save_default=SAVE_DEFAULT,
    ):
        super(TrackSeg, self).__init__()
        self.parent = parent
        self.tree = None

        self.summarise_track_default = summarise_track_default

        # Point / Spline fitting settings
        self.point_size_default = POINT_SIZE  # Keep track of default
        self.point_size = point_size  # Initialise
        self.spline_points_default = spline_points_default
        self.spline_size_default = SPLINE_SIZE  # Keep track of default
        self.spline_size = spline_size  # Initialise
        self.spline_smoothing_default = spline_smoothing_default
        self.fit_degree_default = fit_degree_default
        self.save_default = save_default

        # File formats
        self.track_file_extension = track_file_extension

        # Initialise spline and spline names
        self.splines = None
        self.spline_names = None

    def add_track_panel(self, row):
        self.track_panel = QGroupBox("Track tracing")
        track_layout = QGridLayout()

        add_button(
            "Add track",
            track_layout,
            self.add_track,
            row=6,
            column=0,
            tooltip="Create a new empty segmentation layer "
            "to manually annotate a new track.",
        )

        add_button(
            "Trace tracks",
            track_layout,
            self.run_track_analysis,
            row=6,
            column=1,
            tooltip="Join up the points using a spline fit "
            "and save the distribution of the track in "
            "the brain.",
        )

        add_button(
            "Add track from selected layer",
            track_layout,
            self.add_track_from_existing_layer,
            row=7,
            column=0,
            tooltip="Adds a track from a selected points layer (e.g. "
            "from another plugin). Make sure this track "
            "was segmented from the currently loaded "
            "brainreg result (i.e. atlas/sample space)! ",
        )

        add_button(
            "Add surface points",
            track_layout,
            self.add_surface_points,
            row=7,
            column=1,
            tooltip="Add an additional first point at the surface of the "
            "brain. Selecting this option will add an additional "
            "point at the closest part of the brain surface to the "
            "first point, so that the track starts there.",
        )

        self.summarise_track_checkbox = add_checkbox(
            track_layout,
            self.summarise_track_default,
            "Summarise",
            row=0,
            tooltip="Save a csv file, showing the brain area for "
            "each part of the interpolated track "
            "(determined by the number of spline points). ",
        )
        self.save_checkbox = add_checkbox(
            track_layout,
            self.save_default,
            "Save tracing",
            row=1,
            tooltip="Save the traced layers during analysis.",
        )

        self.fit_degree = add_int_box(
            track_layout,
            self.fit_degree_default,
            2,
            5,
            "Fit degree",
            row=2,
            tooltip="Degree of polynomial to fit to the track.",
        )

        self.spline_smoothing = add_float_box(
            track_layout,
            self.spline_smoothing_default,
            0,
            1,
            "Spline smoothing",
            0.1,
            row=3,
            tooltip="How closely or not to fit the points "
            "(lower numbers fit more closely, for "
            "a less smooth interpolation).",
        )

        self.spline_points = add_int_box(
            track_layout,
            self.spline_points_default,
            1,
            10000,
            "Spline points",
            row=4,
            tooltip="How many points are sampled from the "
            "interpolation (used for the summary).",
        )

        track_layout.setColumnMinimumWidth(1, COLUMN_WIDTH)
        self.track_panel.setLayout(track_layout)
        self.parent.layout.addWidget(self.track_panel, row, 0, 1, 2)
        self.track_panel.setVisible(False)

    def toggle_track_panel(self):
        # TODO: Change color scheme directly when theme is switched
        # TODO: "text-align" property should follow constant
        # SEGM_METHODS_PANEL_ALIGN
        if self.track_panel.isVisible():
            self.track_panel.setVisible(False)
            if self.parent.viewer.theme == "dark":
                self.parent.show_trackseg_button.setStyleSheet(
                    f"QPushButton {{ background-color: #414851; text-align:"
                    f"{SEGM_METHODS_PANEL_ALIGN};}}"
                    f"QPushButton:pressed {{ background-color: #414851; "
                    f"text-align:{SEGM_METHODS_PANEL_ALIGN};}}"
                )
            else:
                self.parent.show_trackseg_button.setStyleSheet(
                    f"QPushButton {{ background-color: #d6d0ce; text-align:"
                    f"{SEGM_METHODS_PANEL_ALIGN};}}"
                    f"QPushButton:pressed {{ background-color: #d6d0ce; "
                    f"text-align:{SEGM_METHODS_PANEL_ALIGN};}}"
                )

        else:
            self.track_panel.setVisible(True)
            if self.parent.viewer.theme == "dark":
                self.parent.show_trackseg_button.setStyleSheet(
                    f"QPushButton {{ background-color: #7e868f; text-align:"
                    f"{SEGM_METHODS_PANEL_ALIGN};}}"
                    f"QPushButton:pressed {{ background-color: #7e868f; "
                    f"text-align:{SEGM_METHODS_PANEL_ALIGN};}}"
                )
            else:
                self.parent.show_trackseg_button.setStyleSheet(
                    f"QPushButton {{ background-color: #fdf194; text-align:"
                    f"{SEGM_METHODS_PANEL_ALIGN};}}"
                    f"QPushButton:pressed {{ background-color: #fdf194; "
                    f"text-align:{SEGM_METHODS_PANEL_ALIGN};}}"
                )

    def check_saved_track(self):
        track_files = glob(
            str(self.parent.paths.tracks_directory)
            + "/*"
            + self.track_file_extension
        )
        if self.parent.paths.tracks_directory.exists() and track_files != []:
            for track_file in track_files:
                self.parent.track_layers.append(
                    add_existing_track_layers(
                        self.parent.viewer,
                        track_file,
                        self.point_size,
                    )
                )

    def add_track(self):
        print("Adding a new track\n")
        self.splines = None
        self.spline_names = None
        self.track_panel.setVisible(True)  # Should be visible by default!
        add_new_track_layer(
            self.parent.viewer,
            self.parent.track_layers,
            self.point_size,
        )

    def add_track_from_existing_layer(self, override=False):
        print("Adding track from existing layer\n")
        selected_layer = self.parent.viewer.layers.selection.active
        try:
            add_track_from_existing_layer(
                selected_layer, self.parent.track_layers
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
                    "Selected layer is not a points layer. "
                    "Please select a points layer and try again.",
                )

    def add_surface_points(self):
        if self.parent.track_layers:
            print("Adding surface points (this may take a while)")
            if self.tree is None:
                self.create_brain_surface_tree()

            for track_layer in self.parent.track_layers:
                try:
                    _, index = self.tree.query(track_layer.data[0])
                except IndexError:
                    print(
                        f"{track_layer.name} does not appear to hold any data"
                    )
                    continue
                surface_point = self.tree.data[index]
                track_layer.data = np.vstack((surface_point, track_layer.data))
            print("Finished!\n")
        else:
            print("No tracks found.")

    def create_brain_surface_tree(self):
        self.tree = create_KDTree_from_image(
            self.parent.annotations_layer.data
        )

    def run_track_analysis(self, override=False):
        if self.parent.track_layers:
            if not override:
                choice = display_warning(
                    self.parent,
                    "About to analyse tracks",
                    "Please ensure the tracks were defined in the same "
                    "reference space as the currently open image. "
                    "Existing files will be will be deleted. Proceed?",
                )
            else:
                choice = True  # for debugging

            if choice:
                if self.save_checkbox.isChecked():
                    self.parent.run_save()

                print("Running track analysis")
                self.splines, self.spline_names = track_analysis(
                    self.parent.viewer,
                    self.parent.annotations_layer.data,
                    self.parent.atlas,
                    self.parent.paths.tracks_directory,
                    self.parent.track_layers,
                    self.spline_size,
                    spline_points=self.spline_points.value(),
                    fit_degree=self.fit_degree.value(),
                    spline_smoothing=self.spline_smoothing.value(),
                    summarise_track=self.summarise_track_checkbox.isChecked(),
                )
                print("Finished!\n")
            else:
                print("Preventing analysis as user chose 'Cancel'")
        else:
            print("No tracks found.")
