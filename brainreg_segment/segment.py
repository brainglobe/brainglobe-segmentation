import napari
import numpy as np

from pathlib import Path
from glob import glob
from napari.qt.threading import thread_worker
from qtpy import QtCore

from qtpy.QtWidgets import (
    QLabel,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QWidget,
)

from bg_atlasapi import BrainGlobeAtlas

from brainreg_segment.paths import Paths

from brainreg_segment.gui_elements import (
    add_button,
    add_checkbox,
    add_float_box,
    add_int_box,
    add_combobox,
)

from brainreg_segment.regions.IO import (
    save_label_layers,
    export_label_layers,
)
from brainreg_segment.regions.layers import (
    add_existing_region_segmentation,
    add_new_region_layer,
)
from brainreg_segment.regions.analysis import region_analysis

from brainreg_segment.tracks.IO import save_track_layers, export_splines
from brainreg_segment.tracks.layers import (
    add_new_track_layer,
    add_existing_track_layers,
)
from brainreg_segment.tracks.analysis import track_analysis

from brainreg_segment.image.utils import create_KDTree_from_image

from brainreg_segment.atlas.utils import (
    get_available_atlases,
    display_brain_region_name,
)


class ManualSegmentationWidget(QWidget):
    def __init__(
        self,
        viewer,
        point_size=100,
        spline_size=50,
        track_file_extension=".points",
        image_file_extension=".tiff",
        num_colors=10,
        brush_size=250,
        spline_points_default=1000,
        spline_smoothing_default=0.1,
        fit_degree_default=3,
        summarise_track_default=True,
        add_surface_point_default=False,
        calculate_volumes_default=True,
        summarise_volumes_default=True,
        boundaries_string="Boundaries",
    ):
        super(ManualSegmentationWidget, self).__init__()
        self.point_size = point_size
        self.spline_size = spline_size
        self.brush_size = brush_size

        # general variables
        self.viewer = viewer

        # track variables
        self.track_layers = []
        self.tree = None
        self.track_file_extension = track_file_extension
        self.spline_points_default = spline_points_default
        self.spline_smoothing_default = spline_smoothing_default
        self.summarise_track_default = summarise_track_default
        self.add_surface_point_default = add_surface_point_default
        self.fit_degree_default = fit_degree_default

        # region variables
        self.label_layers = []
        self.image_file_extension = image_file_extension
        self.num_colors = num_colors
        self.calculate_volumes_default = calculate_volumes_default
        self.summarise_volumes_default = summarise_volumes_default

        # atlas variables
        self.region_labels = []

        self.boundaries_string = boundaries_string
        self.setup_layout()

    def setup_layout(self):
        self.instantiated = False
        self.layout = QGridLayout()
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.setSpacing(4)

        self.add_loading_panel(1)
        self.add_track_panel(2)
        self.add_region_panel(3)
        self.add_saving_panel(4)

        self.status_label = QLabel()
        self.status_label.setText("Ready")
        self.layout.addWidget(self.status_label, 5, 0)

        self.setLayout(self.layout)

    def add_loading_panel(self, row):
        self.load_data_panel = QGroupBox()
        self.load_data_layout = QGridLayout()

        self.load_button = add_button(
            "Load project (sample space)",
            self.load_data_layout,
            self.load_brainreg_directory_sample,
            0,
            0,
            minimum_width=200,
        )

        self.load_button_standard = add_button(
            "Load project (atlas space)",
            self.load_data_layout,
            self.load_brainreg_directory_standard,
            1,
            0,
            minimum_width=200,
        )

        self.load_atlas_button = add_button(
            "Use standalone atlas",
            self.load_data_layout,
            self.setup_atlas,
            2,
            0,
            minimum_width=200,
        )

        self.load_data_layout.setColumnMinimumWidth(1, 150)
        self.load_data_panel.setLayout(self.load_data_layout)
        self.layout.addWidget(self.load_data_panel, row, 0, 1, 2)

        self.load_data_panel.setVisible(True)

    def setup_atlas(self):
        self.atlas_menu, self.atlas_menu_label = self.add_atlas_menu(
            self.load_data_layout
        )
        self.set_output_directory()

    def add_atlas_menu(self, layout):
        list_of_atlasses = [""]
        available_atlases = get_available_atlases()
        for atlas in available_atlases.keys():
            atlas_desc = f"{atlas} v{available_atlases[atlas]}"
            list_of_atlasses.append(atlas_desc)
        atlas_menu, atlas_menu_label = add_combobox(
            layout,
            "Choose atlas",
            list_of_atlasses,
            4,
            label_stack=True,
            callback=self.initialise_atlas,
        )
        atlas_menu.setVisible(False)
        atlas_menu_label.setVisible(False)
        return atlas_menu, atlas_menu_label

    def add_track_panel(self, row):
        self.track_panel = QGroupBox("Track tracing")
        track_layout = QGridLayout()

        add_button(
            "Add track", track_layout, self.add_track, 6, 0,
        )
        add_button(
            "Trace tracks", track_layout, self.run_track_analysis, 6, 1,
        )
        add_button(
            "Add surface points", track_layout, self.add_surface_points, 5, 1,
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

        track_layout.setColumnMinimumWidth(1, 150)
        self.track_panel.setLayout(track_layout)
        self.layout.addWidget(self.track_panel, row, 0, 1, 2)

        self.track_panel.setVisible(False)

    def add_region_panel(self, row):
        self.region_panel = QGroupBox("Region analysis")
        region_layout = QGridLayout()

        add_button(
            "Add region", region_layout, self.add_new_region, 2, 0,
        )
        add_button(
            "Analyse regions", region_layout, self.run_region_analysis, 2, 1,
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

        region_layout.setColumnMinimumWidth(1, 150)
        self.region_panel.setLayout(region_layout)
        self.layout.addWidget(self.region_panel, row, 0, 1, 2)

        self.region_panel.setVisible(False)

    def add_saving_panel(self, row):
        self.save_data_panel = QGroupBox()
        self.save_data_layout = QGridLayout()

        self.export_button = add_button(
            "Export to brainrender",
            self.save_data_layout,
            self.export_to_brainrender,
            0,
            0,
            visibility=False,
        )
        self.save_button = add_button(
            "Save", self.save_data_layout, self.save, 0, 1, visibility=False
        )

        self.save_data_layout.setColumnMinimumWidth(1, 150)
        self.save_data_panel.setLayout(self.save_data_layout)
        self.layout.addWidget(self.save_data_panel, row, 0, 1, 2)

        self.save_data_panel.setVisible(False)

    def initialise_atlas(self, i):
        atlas_string = self.atlas_menu.currentText()
        atlas_name = atlas_string.split(" ")[0].strip()
        atlas = BrainGlobeAtlas(atlas_name)
        self.directory = self.directory / atlas_name
        self.paths = Paths(self.directory, atlas_space=True)

        # raises error
        # self.remove_existing_data()

        self.atlas = atlas
        self.base_layer = self.viewer.add_image(
            self.atlas.reference, name="Reference"
        )
        self.atlas_layer = self.viewer.add_labels(
            self.atlas.annotation,
            name=self.atlas.atlas_name,
            blending="additive",
            opacity=0.3,
            visible=False,
        )
        self.paths = Paths(self.directory, atlas_space=True)
        self.atlas_menu.setVisible(False)
        self.atlas_menu_label.setVisible(False)
        self.standard_space = True
        self.initialise_segmentation_interface()

    def initialise_image_view(self):
        self.set_z_position()

    def set_z_position(self):
        midpoint = int(round(len(self.base_layer.data) / 2))
        self.viewer.dims.set_point(0, midpoint)

    def set_output_directory(self):
        self.status_label.setText("Loading...")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.directory = QFileDialog.getExistingDirectory(
            self, "Select output directory", options=options,
        )
        if self.directory != "":
            self.directory = Path(self.directory)
            self.atlas_menu.setVisible(True)
            self.atlas_menu_label.setVisible(True)

    def load_brainreg_directory_sample(self):
        self.load_brainreg_directory(standard_space=False)

    def load_brainreg_directory_standard(self):
        self.load_brainreg_directory(standard_space=True)

    def load_brainreg_directory(self, standard_space=True):
        if standard_space:
            plugin = "brainreg_standard"
            self.standard_space = True
        else:
            plugin = "brainreg"
            self.standard_space = False

        self.status_label.setText("Loading...")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.directory = QFileDialog.getExistingDirectory(
            self, "Select brainreg directory", options=options,
        )
        if self.directory != "":
            try:
                self.directory = Path(self.directory)
                # self.remove_existing_data()

                self.viewer.open(str(self.directory), plugin=plugin)
                self.paths = Paths(
                    self.directory, standard_space=standard_space,
                )

                self.initialise_loaded_data()
            except ValueError:
                print(
                    f"The directory ({self.directory}) does not appear to be "
                    f"a brainreg directory, please try again."
                )

    def remove_existing_data(self):
        if len(self.viewer.layers) != 0:
            # remove old layers
            for layer in list(self.viewer.layers):
                self.viewer.layers.remove(layer)

    def initialise_loaded_data(self):
        # for consistency, don't load this
        try:
            self.viewer.layers.remove(self.boundaries_string)
        except KeyError:
            pass

        self.base_layer = self.viewer.layers["Registered image"]
        self.metadata = self.base_layer.metadata
        self.atlas = self.metadata["atlas_class"]
        self.atlas_layer = self.viewer.layers[self.metadata["atlas"]]
        self.initialise_segmentation_interface()

    def initialise_segmentation_interface(self):
        self.reset_variables()
        self.initialise_image_view()

        @self.atlas_layer.mouse_move_callbacks.append
        def display_region_name(layer, event):
            display_brain_region_name(layer, self.atlas.structures)

        self.load_button.setMinimumWidth(0)
        self.save_data_panel.setVisible(True)
        self.save_button.setVisible(True)
        self.export_button.setVisible(self.standard_space)
        self.initialise_region_segmentation()
        self.initialise_track_tracing()
        self.status_label.setText("Ready")

    def reset_variables(self):
        self.mean_voxel_size = int(
            np.sum(self.atlas.resolution) / len(self.atlas.resolution)
        )
        self.point_size = self.point_size / self.mean_voxel_size
        self.spline_size = self.spline_size / self.mean_voxel_size
        self.brush_size = self.brush_size / self.mean_voxel_size

    def initialise_track_tracing(self):
        track_files = glob(
            str(self.paths.tracks_directory) + "/*" + self.track_file_extension
        )
        if self.paths.tracks_directory.exists() and track_files != []:
            for track_file in track_files:
                self.track_layers.append(
                    add_existing_track_layers(
                        self.viewer, track_file, self.point_size,
                    )
                )
        self.track_panel.setVisible(True)
        self.region_panel.setVisible(True)
        self.splines = None

    def add_track(self):
        print("Adding a new track\n")
        add_new_track_layer(self.viewer, self.track_layers, self.point_size)

    def add_surface_points(self):
        if self.track_layers:
            print("Adding surface points")
            if self.tree is None:
                self.create_brain_surface_tree()

            for track_layer in self.track_layers:
                _, index = self.tree.query(track_layer.data[0])
                surface_point = self.tree.data[index]
                track_layer.data = np.vstack((surface_point, track_layer.data))
            print("Finished!\n")
        else:
            print("No tracks found.")

    def create_brain_surface_tree(self):
        self.tree = create_KDTree_from_image(self.atlas_layer.data)

    def run_track_analysis(self):
        if self.track_layers:
            print("Running track analysis")
            try:
                self.splines, self.spline_names = track_analysis(
                    self.viewer,
                    self.atlas,
                    self.paths.tracks_directory,
                    self.track_layers,
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

    def initialise_region_segmentation(self):
        add_existing_region_segmentation(
            self.paths.regions_directory,
            self.viewer,
            self.label_layers,
            self.image_file_extension,
        )

    def add_new_region(self):
        print("Adding a new region\n")
        add_new_region_layer(
            self.viewer,
            self.label_layers,
            self.base_layer.data,
            self.brush_size,
            self.num_colors,
        )

    def run_region_analysis(self):
        if self.label_layers:
            print("Running region analysis")
            worker = region_analysis(
                self.label_layers,
                self.atlas_layer.data,
                self.atlas,
                self.paths.regions_directory,
                output_csv_file=self.paths.region_summary_csv,
                volumes=self.calculate_volumes_checkbox.isChecked(),
                summarise=self.summarise_volumes_checkbox.isChecked(),
            )
            worker.start()
        else:
            print("No regions found")

    def save(self):
        if self.label_layers or self.track_layers:
            print("Saving")
            worker = save_all(
                self.paths.regions_directory,
                self.paths.tracks_directory,
                self.label_layers,
                self.track_layers,
                track_file_extension=self.track_file_extension,
            )
            worker.start()

    def export_to_brainrender(self):
        print("Exporting")
        max_axis_2 = self.base_layer.shape[2]
        worker = export_all(
            self.paths.regions_directory,
            self.paths.tracks_directory,
            self.label_layers,
            self.splines,
            self.spline_names,
            self.atlas.resolution[0],
            max_axis_2,
        )
        worker.start()


@thread_worker
def export_all(
    regions_directory,
    tracks_directory,
    label_layers,
    splines,
    spline_names,
    resolution,
    max_axis_2,
):
    if label_layers:
        export_label_layers(regions_directory, label_layers)

    if splines:
        export_splines(
            tracks_directory, splines, spline_names, resolution, max_axis_2
        )
    print("Finished!\n")


@thread_worker
def save_all(
    regions_directory,
    tracks_directory,
    label_layers,
    points_layers,
    track_file_extension=".points",
):
    if label_layers:
        save_label_layers(regions_directory, label_layers)

    if points_layers:
        save_track_layers(
            tracks_directory,
            points_layers,
            track_file_extension=track_file_extension,
        )
    print("Finished!\n")


def main():
    print("Loading manual segmentation GUI.\n ")
    with napari.gui_qt():

        viewer = napari.Viewer(title="Manual segmentation")
        general = ManualSegmentationWidget(viewer)
        viewer.window.add_dock_widget(general, name="General", area="right")


if __name__ == "__main__":
    main()
