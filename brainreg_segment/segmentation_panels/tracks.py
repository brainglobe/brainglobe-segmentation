# TrackSeg
from glob import glob
import numpy as np

from qtpy.QtWidgets import (
    QGridLayout,
    QGroupBox,
)

from brainreg_segment.layout.gui_elements import (
    add_button,
    add_checkbox,
    add_float_box,
    add_int_box,
)
from brainreg_segment.tracks.layers import (
    add_new_track_layer,
    add_existing_track_layers,
)
from brainreg_segment.image.utils import create_KDTree_from_image

from brainreg_segment.tracks.analysis import track_analysis
from brainreg_segment.layout.gui_constants import (
    COLUMN_WIDTH,
    POINT_SIZE,
    SPLINE_SIZE,
    TRACK_FILE_EXT,
    SPLINE_POINTS_DEFAULT,
    SPLINE_SMOOTHING_DEFAULT,
    FIT_DEGREE_DEFAULT,
    SUMMARISE_TRACK_DEFAULT,
    ADD_SURFACE_POINT_DEFAULT,
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
        add_surface_point_default=ADD_SURFACE_POINT_DEFAULT,
    ):

        super(TrackSeg, self).__init__()
        self.parent = parent
        self.tree = None

        self.summarise_track_default = summarise_track_default
        self.add_surface_point_default = add_surface_point_default

        # Point / Spline fitting settings
        self.point_size = point_size
        self.spline_points_default = spline_points_default
        self.spline_size = spline_size
        self.spline_smoothing_default = spline_smoothing_default
        self.fit_degree_default = fit_degree_default

        # File formats
        self.track_file_extension = track_file_extension

        # Initialise spline and spline names
        self.splines = None
        self.spline_names = None

    def add_track_panel(self, row):
        self.track_panel = QGroupBox("Track tracing")
        track_layout = QGridLayout()

        add_button(
            "Add surface points", track_layout, self.add_surface_points, 5, 1,
        )

        add_button(
            "Add track", track_layout, self.add_track, 6, 0,
        )

        add_button(
            "Trace tracks", track_layout, self.run_track_analysis, 6, 1,
        )

        self.summarise_track_checkbox = add_checkbox(
            track_layout, self.summarise_track_default, "Summarise", 0,
        )

        self.add_surface_point_checkbox = add_checkbox(
            track_layout,
            self.add_surface_point_default,
            "Add surface point",
            1,
        )

        self.fit_degree = add_int_box(
            track_layout, self.fit_degree_default, 1, 5, "Fit degree", 2,
        )

        self.spline_smoothing = add_float_box(
            track_layout,
            self.spline_smoothing_default,
            0,
            1,
            "Spline smoothing",
            0.1,
            3,
        )

        self.spline_points = add_int_box(
            track_layout,
            self.spline_points_default,
            1,
            10000,
            "Spline points",
            4,
        )

        track_layout.setColumnMinimumWidth(1, COLUMN_WIDTH)
        self.track_panel.setLayout(track_layout)
        self.parent.layout.addWidget(self.track_panel, row, 0, 1, 2)
        self.track_panel.setVisible(False)

    def toggle_track_panel(self):
        # TODO: Change color scheme directly when theme is switched
        # TODO: "text-align" property should follow constant SEGM_METHODS_PANEL_ALIGN
        if self.track_panel.isVisible():
            self.track_panel.setVisible(False)
            if self.parent.viewer.theme == "dark":
                self.parent.show_trackseg_button.setStyleSheet(
                    "QPushButton { background-color: #414851; text-align:left;}"
                    "QPushButton:pressed { background-color: #414851; text-align:left;}"
                )
            else:
                self.parent.show_trackseg_button.setStyleSheet(
                    "QPushButton { background-color: #d6d0ce; text-align:left;}"
                    "QPushButton:pressed { background-color: #d6d0ce; text-align:left;}"
                )

        else:
            self.track_panel.setVisible(True)
            if self.parent.viewer.theme == "dark":
                self.parent.show_trackseg_button.setStyleSheet(
                    "QPushButton { background-color: #7e868f; text-align:left;}"
                    "QPushButton:pressed { background-color: #7e868f; text-align:left;}"
                )
            else:
                self.parent.show_trackseg_button.setStyleSheet(
                    "QPushButton { background-color: #fdf194; text-align:left;}"
                    "QPushButton:pressed { background-color: #fdf194; text-align:left;}"
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
                        self.parent.viewer, track_file, self.point_size,
                    )
                )

    def add_track(self):
        print("Adding a new track\n")
        self.splines = None
        self.spline_names = None
        self.track_panel.setVisible(True)  # Should be visible by default!
        add_new_track_layer(
            self.parent.viewer, self.parent.track_layers, self.point_size,
        )

    def add_surface_points(self):
        if self.parent.track_layers:
            print("Adding surface points")
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
                if len(track_layer.data) != 0:
                    _, index = self.tree.query(track_layer.data[0])
                    surface_point = self.tree.data[index]
                    track_layer.data = np.vstack(
                        (surface_point, track_layer.data)
                    )
            print("Finished!\n")
        else:
            print("No tracks found.")

    def create_brain_surface_tree(self):
        self.tree = create_KDTree_from_image(self.parent.atlas_layer.data)

    def run_track_analysis(self):
        if self.parent.track_layers:
            print("Running track analysis")
            try:
                self.splines, self.spline_names = track_analysis(
                    self.parent.viewer,
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
            except TypeError:
                print(
                    "The number of points must be greater "
                    "than the fit degree. \n"
                    "Please add points, or reduce the fit degree."
                )
        else:
            print("No tracks found.")
