import napari
import numpy as np
from pathlib import Path
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

from brainreg_segment.regions.IO import (
    save_label_layers,
    export_label_layers,
)

from brainreg_segment.tracks.IO import save_track_layers, export_splines

from brainreg_segment.atlas.utils import (
    get_available_atlases,
    structure_from_viewer,
)
from brainreg_segment.layout.utils import display_warning

# LAYOUT HELPERS ################################################################################

# from brainreg_segment.layout.utils import (
#     disable_napari_key_bindings,
#     disable_napari_btns,
#     overwrite_napari_roll,
# )
from brainreg_segment.layout.gui_constants import (
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    COLUMN_WIDTH,
    SEGM_METHODS_PANEL_ALIGN,
    LOADING_PANEL_ALIGN,
    BOUNDARIES_STRING,
    TRACK_FILE_EXT,
    DISPLAY_REGION_INFO,
)

from brainreg_segment.layout.gui_elements import (
    add_button,
    add_combobox,
)

# SEGMENTATION  ################################################################################
from brainreg_segment.segmentation_panels.regions import RegionSeg
from brainreg_segment.segmentation_panels.tracks import TrackSeg


class SegmentationWidget(QWidget):
    def __init__(
        self,
        viewer: napari.viewer.Viewer,
        boundaries_string=BOUNDARIES_STRING,
    ):
        super(SegmentationWidget, self).__init__()

        # general variables
        self.viewer = viewer

        # Disable / overwrite napari viewer functions
        # that either do not make sense or should be avoided by the user
        # removed for now, to make sure plugin
        # disable_napari_btns(self.viewer)
        # disable_napari_key_bindings()
        # overwrite_napari_roll(self.viewer)

        # Main layers
        self.base_layer = []  # Contains registered brain / reference brain
        self.atlas_layer = []  # Contains annotations / region information

        # Other data
        self.hemispheres_data = []

        # Track variables
        self.track_layers = []

        # Region variables
        self.label_layers = []

        # Atlas variables
        self.current_atlas_name = ""
        self.atlas = None

        self.boundaries_string = boundaries_string
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
                    if len(v.layers) and self.atlas_layer and self.atlas:
                        _, _, _, region_info = structure_from_viewer(
                            self.viewer.status, self.atlas_layer, self.atlas
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
            0,
            1,
            minimum_width=COLUMN_WIDTH,
            alignment=SEGM_METHODS_PANEL_ALIGN,
        )
        self.show_trackseg_button.setEnabled(False)

        self.show_regionseg_button = add_button(
            "Region segmentation",
            self.toggle_methods_layout,
            self.region_seg.toggle_region_panel,
            1,
            1,
            minimum_width=COLUMN_WIDTH,
            alignment=SEGM_METHODS_PANEL_ALIGN,
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
            0,
            0,
            visibility=False,
            minimum_width=COLUMN_WIDTH,
            alignment=LOADING_PANEL_ALIGN,
        )

        self.load_button_standard = add_button(
            "Load project (atlas space)",
            self.load_data_layout,
            self.load_brainreg_directory_standard,
            1,
            0,
            visibility=False,
            minimum_width=COLUMN_WIDTH,
            alignment=LOADING_PANEL_ALIGN,
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
            0,
            0,
            visibility=False,
        )
        self.save_button = add_button(
            "Save", self.save_data_layout, self.save, 0, 1, visibility=False
        )

        self.save_data_layout.setColumnMinimumWidth(1, COLUMN_WIDTH)
        self.save_data_panel.setLayout(self.save_data_layout)
        self.layout.addWidget(self.save_data_panel, row, 0, 1, 2)

        self.save_data_panel.setVisible(False)

    # ATLAS INTERACTION ####################################################

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
                2,
                0,
                label_stack=True,
                callback=self.initialise_atlas,
                width=COLUMN_WIDTH,
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
        # self.viewer.title = f"Atlas: {self.current_atlas_name}"
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
        self.atlas_layer = self.viewer.add_labels(
            self.atlas.annotation,
            name=self.atlas.atlas_name,
            blending="additive",
            opacity=0.3,
            visible=False,
        )
        self.standard_space = True

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
            self.plugin = "brainreg-standard"
            self.standard_space = True
        else:
            self.plugin = "brainglobe-io"
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
        self.atlas_layer = self.viewer.layers[self.metadata["atlas"]]
        if self.standard_space:
            self.hemispheres_data = self.atlas.hemispheres
        else:
            self.hemispheres_data = self.viewer.layers["Hemispheres"].data

        self.initialise_segmentation_interface()

        # Set window title
        # self.viewer.title = (
        #     f"Brainreg: {self.metadata['atlas']} ({self.plugin})"
        # )
        self.status_label.setText("Ready")

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
        if len(self.viewer.layers) != 0:
            # Check with user if that is really what is wanted
            if self.track_layers or self.label_layers:
                choice = display_warning(
                    self,
                    "About to remove layers",
                    "All layers are about to be deleted. Proceed?",
                )
                if not choice:
                    print('Preventing deletion because user chose "Cancel"')
                    return False

            # Remove old layers
            for layer in list(self.viewer.layers):
                try:
                    self.viewer.layers.remove(layer)
                except IndexError:  # no idea why this happens
                    pass

        # There seems to be a napari bug trying to access previously used slider
        # values. Trying to circument for now
        self.viewer.window.qt_viewer.dims._last_used = None

        self.track_layers = []
        self.label_layers = []
        return True

    def save(self):
        if self.label_layers or self.track_layers:
            choice = display_warning(
                self,
                "About to save files",
                "Existing files will be will be deleted. Proceed?",
            )
            if choice:
                print("Saving")
                worker = save_all(
                    self.paths.regions_directory,
                    self.paths.tracks_directory,
                    self.label_layers,
                    self.track_layers,
                    track_file_extension=TRACK_FILE_EXT,
                )
                worker.start()
            else:
                print('Not saving because user chose "Cancel" \n')

    def export_to_brainrender(self):
        choice = display_warning(
            self,
            "About to export files",
            "Existing files will be will be deleted. Proceed?",
        )
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
