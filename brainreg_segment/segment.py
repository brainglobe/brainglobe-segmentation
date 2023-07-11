from pathlib import Path
from typing import List, Optional

import napari
import numpy as np
from bg_atlasapi import BrainGlobeAtlas
from napari.qt.threading import thread_worker
from qtpy import QtCore
from qtpy.QtWidgets import QFileDialog, QGridLayout, QGroupBox, QLabel, QWidget

from brainreg_segment.atlas.utils import (
    get_available_atlases,
    structure_from_viewer,
)
from brainreg_segment.layout.gui_constants import (
    BOUNDARIES_STRING,
    COLUMN_WIDTH,
    DISPLAY_REGION_INFO,
    HEMISPHERES_STRING,
    LOADING_PANEL_ALIGN,
    SEGM_METHODS_PANEL_ALIGN,
    TRACK_FILE_EXT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from brainreg_segment.layout.gui_elements import add_button, add_combobox
from brainreg_segment.layout.utils import display_warning
from brainreg_segment.paths import Paths
from brainreg_segment.regions.IO import export_label_layers, save_label_layers

### SEGMENTATION
from brainreg_segment.segmentation_panels.regions import RegionSeg
from brainreg_segment.segmentation_panels.tracks import TrackSeg
from brainreg_segment.tracks.IO import export_splines, save_track_layers

### LAYOUT HELPERS


class SegmentationWidget(QWidget):
    def __init__(
        self,
        viewer: napari.viewer.Viewer,
        boundaries_string=BOUNDARIES_STRING,
        hemispheres_string=HEMISPHERES_STRING,
    ):
        super(SegmentationWidget, self).__init__()

        # general variables
        self.viewer = viewer

        # Main layers

        # Contains registered brain / reference brain
        self.base_layer: Optional[napari.layers.Image] = None
        # Contains annotations / region information
        self.annotations_layer: Optional[napari.layers.Labels] = None

        # Other data
        self.hemispheres_layer: Optional[napari.layers.Labels] = None
        self.hemispheres_data: Optional[np.ndarray] = None

        # Track variables
        self.track_layers: List[napari.layers.Tracks] = []

        # Region variables
        self.label_layers: List[napari.layers.Labels] = []

        # List of all layers created by plugin, to allow the correct
        # layers to be modified
        self.editable_widget_layers: List[napari.layers.Layer] = []
        self.non_editable_widget_layers: List[napari.layers.Layer] = []

        # Atlas variables
        self.current_atlas_name = ""
        self.atlas = None

        self.boundaries_string = boundaries_string
        self.hemispheres_string = hemispheres_string

        self.directory = ""
        # Set up segmentation methods
        self.region_seg = RegionSeg(self)
        self.track_seg = TrackSeg(self)

        # Generate main layout
        self.setup_main_layout()

        if DISPLAY_REGION_INFO:

            @self.viewer.mouse_move_callbacks.append
            def display_region_info(v, event):
                """
                Show brain region info on mouse over in status bar on the right
                """
                assert self.viewer == v
                if v.dims.ndisplay == 2:
                    if len(v.layers) and self.annotations_layer and self.atlas:
                        _, _, _, region_info = structure_from_viewer(
                            self.viewer.cursor.position,
                            self.annotations_layer,
                            self.atlas,
                        )
                        self.viewer.help = region_info
                else:
                    self.viewer.help = ""

    def setup_main_layout(self):
        """
        Construct main layout of widget
        """
        self.layout = QGridLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.setSpacing(4)

        # 3 Steps:
        # - Loading panel
        # - Segmentation methods panel
        # -> Individual segmentation methods (which are invisible at first)
        # - Saving panel

        self.add_loading_panel(1)
        self.add_segmentation_methods_panel(1)
        self.track_seg.add_track_panel(2)  # Track segmentation subpanel
        self.region_seg.add_region_panel(3)  # Region segmentation subpanel
        self.add_saving_panel(4)

        # Take care of status label
        self.status_label = QLabel()
        self.status_label.setText("Ready")
        self.layout.addWidget(self.status_label, 5, 0)

        self.setLayout(self.layout)

    # PANELS ###############################################################

    def add_segmentation_methods_panel(self, row, column=1):
        """
        Segmentation methods chooser panel:
            Toggle visibility of segmentation
            methods
        """
        self.toggle_methods_panel = QGroupBox("Segmentation")
        self.toggle_methods_layout = QGridLayout()
        self.toggle_methods_layout.setContentsMargins(10, 10, 10, 10)
        self.toggle_methods_layout.setSpacing(5)
        self.toggle_methods_layout.setAlignment(QtCore.Qt.AlignBottom)

        self.show_trackseg_button = add_button(
            "Track tracing",
            self.toggle_methods_layout,
            self.track_seg.toggle_track_panel,
            row=0,
            column=1,
            minimum_width=COLUMN_WIDTH,
            alignment=SEGM_METHODS_PANEL_ALIGN,
            tooltip="Segment a 1D structure (e.g. an axon "
            "or implanted electrode)",
        )
        self.show_trackseg_button.setEnabled(False)

        self.show_regionseg_button = add_button(
            "Region segmentation",
            self.toggle_methods_layout,
            self.region_seg.toggle_region_panel,
            row=1,
            column=1,
            minimum_width=COLUMN_WIDTH,
            alignment=SEGM_METHODS_PANEL_ALIGN,
            tooltip="Segment a 2/3D structure (e.g. a brain region)",
        )
        self.show_regionseg_button.setEnabled(False)

        self.toggle_methods_layout.setColumnMinimumWidth(1, COLUMN_WIDTH)
        self.toggle_methods_panel.setLayout(self.toggle_methods_layout)
        self.toggle_methods_panel.setVisible(True)

        self.layout.addWidget(self.toggle_methods_panel, row, column, 1, 1)

    def add_loading_panel(self, row, column=0):
        """
        Loading panel:
            - Load project (sample space)
            - Load project (atlas space)
            - Atlas chooser
        """
        self.load_data_panel = QGroupBox("Load data")
        self.load_data_layout = QGridLayout()
        self.load_data_layout.setSpacing(15)
        self.load_data_layout.setContentsMargins(10, 10, 10, 10)
        self.load_data_layout.setAlignment(QtCore.Qt.AlignBottom)

        self.load_button = add_button(
            "Load project (sample space)",
            self.load_data_layout,
            self.load_brainreg_directory_sample,
            row=0,
            column=0,
            visibility=False,
            minimum_width=COLUMN_WIDTH,
            alignment=LOADING_PANEL_ALIGN,
            tooltip="Load a brainreg project in the coordinate "
            "space of your raw data (i.e., not warped to the atlas "
            "space).  N.B. the data will have been reoriented to "
            "the orientation of your chosen atlas.",
        )

        self.load_button_standard = add_button(
            "Load project (atlas space)",
            self.load_data_layout,
            self.load_brainreg_directory_standard,
            row=1,
            column=0,
            visibility=False,
            minimum_width=COLUMN_WIDTH,
            alignment=LOADING_PANEL_ALIGN,
            tooltip="Load a brainreg project warped to the coordinate "
            "space of the atlas.",
        )

        self.add_atlas_menu(self.load_data_layout)

        self.load_data_layout.setColumnMinimumWidth(0, COLUMN_WIDTH)
        self.load_data_panel.setLayout(self.load_data_layout)
        self.load_data_panel.setVisible(True)

        self.layout.addWidget(self.load_data_panel, row, column, 1, 1)

        #  buttons made visible after adding to main widget, preventing them
        # from briefly appearing in a separate window
        self.load_button.setVisible(True)
        self.load_button_standard.setVisible(True)

    def add_saving_panel(self, row):
        """
        Saving/Export panel
        """
        self.save_data_panel = QGroupBox()
        self.save_data_layout = QGridLayout()

        self.export_button = add_button(
            "To brainrender",
            self.save_data_layout,
            self.export_to_brainrender,
            row=0,
            column=0,
            visibility=False,
            tooltip="Export the segmentation to brainrender "
            "(only works if the segmentation was "
            "performed in atlas space.",
        )
        self.save_button = add_button(
            "Save",
            self.save_data_layout,
            self.save,
            row=0,
            column=1,
            visibility=False,
            tooltip="Save the segmentation to disk to " "be reloaded later.",
        )

        self.save_data_layout.setColumnMinimumWidth(1, COLUMN_WIDTH)
        self.save_data_panel.setLayout(self.save_data_layout)
        self.layout.addWidget(self.save_data_panel, row, 0, 1, 2)

        self.save_data_panel.setVisible(False)

    # ATLAS INTERACTION ###################################################

    def add_atlas_menu(self, layout):
        list_of_atlasses = ["Load atlas"]
        available_atlases = get_available_atlases()
        for atlas in available_atlases.keys():
            atlas_desc = f"{atlas} v{available_atlases[atlas]}"
            list_of_atlasses.append(atlas_desc)
            atlas_menu, _ = add_combobox(
                layout,
                None,
                list_of_atlasses,
                row=2,
                column=0,
                label_stack=True,
                callback=self.initialise_atlas,
                width=COLUMN_WIDTH,
                tooltip="Load a BrainGlobe atlas if you don't have "
                "a brainreg project to load. Useful for creating "
                "illustrations or testing the software.",
            )

        self.atlas_menu = atlas_menu

    def initialise_atlas(self):
        atlas_string = self.atlas_menu.currentText()
        atlas_name = atlas_string.split(" ")[0].strip()
        if atlas_name != self.current_atlas_name:
            status = self.remove_layers()
            if not status:  # Something prevented deletion
                self.reset_atlas_menu()
                return
        else:
            print(f"{atlas_string} already selected for segmentation.")
            self.reset_atlas_menu()
            return

        # Get / set output directory
        self.set_output_directory()
        if not self.directory:
            self.reset_atlas_menu()
            return

        self.current_atlas_name = atlas_name
        # Instantiate atlas layers
        self.load_atlas()

        self.directory = self.directory / atlas_name
        self.paths = Paths(self.directory, atlas_space=True)

        self.status_label.setText("Ready")
        # Set window title
        self.initialise_segmentation_interface()
        # Check / load previous regions and tracks
        self.region_seg.check_saved_region()
        self.track_seg.check_saved_track()
        self.reset_atlas_menu()

    def set_output_directory(self):
        self.status_label.setText("Loading...")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.directory = QFileDialog.getExistingDirectory(
            self,
            "Select output directory",
            options=options,
        )
        if self.directory != "":
            self.directory = Path(self.directory)

    def load_atlas(self):
        atlas = BrainGlobeAtlas(self.current_atlas_name)
        self.atlas = atlas
        self.base_layer = self.viewer.add_image(
            self.atlas.reference,
            name="Reference",
        )
        self.annotations_layer = self.viewer.add_labels(
            self.atlas.annotation,
            name=self.atlas.atlas_name,
            blending="additive",
            opacity=0.3,
            visible=False,
        )
        self.standard_space = True
        self.prevent_layer_edit()

    def reset_atlas_menu(self):
        # Reset menu for atlas - show initial description
        self.atlas_menu.blockSignals(True)
        self.atlas_menu.setCurrentIndex(0)
        self.atlas_menu.blockSignals(False)

    # BRAINREG INTERACTION #################################################

    def load_brainreg_directory_sample(self):
        self.get_brainreg_directory(standard_space=False)

    def load_brainreg_directory_standard(self):
        self.get_brainreg_directory(standard_space=True)

    def get_brainreg_directory(self, standard_space):
        """
        Shows file dialog to choose output directory
        and sets global directory info
        """
        if standard_space:
            self.plugin = (
                "brainglobe-napari-io.brainreg_read_dir_standard_space"
            )
            self.standard_space = True
        else:
            self.plugin = "brainglobe-napari-io.brainreg_read_dir"
            self.standard_space = False

        self.status_label.setText("Loading...")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        brainreg_directory = QFileDialog.getExistingDirectory(
            self,
            "Select brainreg directory",
            options=options,
        )

        if not brainreg_directory:
            return

        if self.directory != brainreg_directory:
            status = self.remove_layers()
            if not status:
                return  # Something prevented deletion
            self.directory = Path(brainreg_directory)
        else:
            print(f"{str(brainreg_directory)} already loaded.")
            return

        # Otherwise, proceed loading brainreg dir
        self.load_brainreg_directory()

    def load_brainreg_directory(self):
        """
        Opens brainreg folder in napari.
        Calls initialise_loaded_data to set up layers / info.
        Then checks for previously loaded data.

        """
        try:
            self.viewer.open(str(self.directory), plugin=self.plugin)
            self.paths = Paths(
                self.directory,
                standard_space=self.standard_space,
            )
            self.initialise_loaded_data()
        except ValueError:
            print(
                f"The directory ({self.directory}) does not appear to be "
                f"a brainreg directory, please try again."
            )
            return

        # Check / load previous regions and tracks
        self.region_seg.check_saved_region()
        self.track_seg.check_saved_track()

    def initialise_loaded_data(self):
        """
        Set up brainreg layers in napari / fill with new data and info

        """
        try:
            self.viewer.layers.remove(self.boundaries_string)
        except ValueError:
            pass

        self.base_layer = self.viewer.layers["Registered image"]
        self.metadata = self.base_layer.metadata
        self.atlas = self.metadata["atlas_class"]
        self.annotations_layer = self.viewer.layers[self.metadata["atlas"]]
        if self.standard_space:
            self.hemispheres_data = self.atlas.hemispheres
        else:
            self.hemispheres_layer = self.viewer.layers[
                self.hemispheres_string
            ]
            self.hemispheres_data = self.hemispheres_layer.data

        self.initialise_segmentation_interface()
        self.status_label.setText("Ready")
        self.prevent_layer_edit()

    def collate_widget_layers(self):
        """
        Populate self.editable_widget_layers and
        self.non_editable_widget_layers.
        """
        self.non_editable_widget_layers = [
            self.base_layer,
            self.annotations_layer,
            self.hemispheres_layer,
        ]
        self.editable_widget_layers = self.track_layers + self.label_layers

        # add any downsampled layers loaded by plugin
        for layer in self.viewer.layers:
            if "downsampled" in layer.name:
                self.non_editable_widget_layers.append(layer)

        # ensure only napari layers in list (i.e. not None etc)
        self.editable_widget_layers = [
            item
            for item in self.editable_widget_layers
            if isinstance(item, napari.layers.Layer)
        ]
        self.non_editable_widget_layers = [
            item
            for item in self.non_editable_widget_layers
            if isinstance(item, napari.layers.Layer)
        ]

    def prevent_layer_edit(self):
        print("Preventing layer edit")
        self.collate_widget_layers()
        for layer in self.non_editable_widget_layers:
            layer.editable = False

    # MORE LAYOUT COMPONENTS ###########################################

    def initialise_segmentation_interface(self):
        self.reset_variables()
        self.initialise_image_view()
        self.save_data_panel.setVisible(True)
        self.save_button.setVisible(True)
        self.export_button.setVisible(self.standard_space)
        self.show_regionseg_button.setEnabled(True)
        self.show_trackseg_button.setEnabled(True)
        self.status_label.setText("Ready")

    def initialise_image_view(self):
        self.set_z_position()

    def set_z_position(self):
        midpoint = int(round(len(self.base_layer.data) / 2))
        self.viewer.dims.set_point(0, midpoint)

    def reset_variables(self):
        """
        Reset atlas scale dependent variables
        - point_size (Track segmentation)
        - spline_size (Track segmentation)
        - brush_size (Region segmentation)
        """
        self.mean_voxel_size = int(
            np.sum(self.atlas.resolution) / len(self.atlas.resolution)
        )
        self.track_seg.point_size = (
            self.track_seg.point_size_default / self.mean_voxel_size
        )
        self.track_seg.spline_size = (
            self.track_seg.spline_size_default / self.mean_voxel_size
        )
        self.region_seg.brush_size = (
            self.region_seg.brush_size_default / self.mean_voxel_size
        )
        return

    def remove_layers(self):
        """
        TODO: This needs work. Runs into an error currently
        when switching from a annotated project to another one
        """
        self.collate_widget_layers()
        all_layers = (
            self.editable_widget_layers + self.non_editable_widget_layers
        )
        if len(all_layers) != 0:
            # Check with user if that is really what is wanted
            choice = display_warning(
                self,
                "About to remove layers",
                "All layers are about to be deleted. Proceed?",
            )
            if not choice:
                print('Preventing deletion because user chose "Cancel"')
                return False

            # Remove old layers
            for layer in all_layers:
                self.viewer.layers.remove(layer)
                self.track_layers = []
                self.label_layers = []
        return True

    def save(self, override=True):
        if self.label_layers or self.track_layers:
            if not override:
                choice = display_warning(
                    self,
                    "About to save files",
                    "Existing files will be will be deleted. Proceed?",
                )
            else:
                choice = True  # for debugging
            if choice:
                self.run_save()
            else:
                print('Not saving because user chose "Cancel" \n')

    def run_save(self):
        print("Saving")
        worker = save_all(
            self.paths.regions_directory,
            self.paths.tracks_directory,
            self.label_layers,
            self.track_layers,
            track_file_extension=TRACK_FILE_EXT,
        )
        worker.start()

    def export_to_brainrender(self, override=False):
        if not override:
            choice = display_warning(
                self,
                "About to export files",
                "Existing files will be will be deleted. Proceed?",
            )
        else:
            choice = True  # for debugging

        if choice:
            print("Exporting")
            worker = export_all(
                self.paths.regions_directory,
                self.paths.tracks_directory,
                self.label_layers,
                self.track_seg.splines,
                self.track_seg.spline_names,
                self.atlas.resolution[0],
            )
            worker.start()
        else:
            print('Not exporting because user chose "Cancel" \n')


@thread_worker
def export_all(
    regions_directory,
    tracks_directory,
    label_layers,
    splines,
    spline_names,
    resolution,
):
    if label_layers:
        export_label_layers(regions_directory, label_layers, resolution)

    if splines:
        export_splines(tracks_directory, splines, spline_names, resolution)
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
    print("Loading segmentation GUI.\n ")
    with napari.gui_qt():
        viewer = napari.Viewer()  # title="Segmentation GUI")
        viewer.window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        widget = SegmentationWidget(viewer)
        viewer.window.add_dock_widget(widget, name="General", area="right")


if __name__ == "__main__":
    main()
