# Small layout utils
# import napari
from napari.viewer import Viewer

import bg_space as bg

# from brainreg_segment.layout.gui_constants import ORIENTATIONS

from qtpy.QtWidgets import QMessageBox


def disable_napari_btns(viewer):
    """
    Disable some Napari functions to hide them from user interation
    - Transpose TODO: Understand how to add this properly with space conventions
    - Grid view
    - Console
    - New labels layer
    - New points layer
    - New shapes layer

    """
    viewer.window.qt_viewer.viewerButtons.transposeDimsButton.setVisible(False)
    viewer.window.qt_viewer.viewerButtons.gridViewButton.setVisible(False)
    viewer.window.qt_viewer.viewerButtons.consoleButton.setVisible(False)
    viewer.window.qt_viewer.layerButtons.newLabelsButton.setVisible(False)
    viewer.window.qt_viewer.layerButtons.newPointsButton.setVisible(False)
    viewer.window.qt_viewer.layerButtons.newShapesButton.setVisible(False)


def disable_napari_key_bindings():
    """
    Disable some default key bingings that are unused
    """

    @Viewer.bind_key("Control-G", overwrite=True)
    def no_grid_mode_warning(self):
        print("Grid mode is not supported")

    @Viewer.bind_key("Control-T", overwrite=True)
    def no_tranpose_warning(self):
        print("Transposing is not supported")


def get_dims_from_origins(origins):
    """From a list of BG space abbreviations (e.g. ["asl","sla","lsa"]) get correct axes for display in Napari"""
    all_dims = []
    for o in range(len(origins)):
        sc = bg.AnatomicalSpace(origins[0])
        next_orientation = origins[(o + 1) % len(origins)]
        dims, flips, _, _ = sc.map_to(next_orientation)
        assert not any(
            flips
        ), f"\nReceived orientations: {origins}\nThese require (orientation) flips. This is not currently supported"
        all_dims.append(list(dims))
    return all_dims


def display_warning(widget, title, message):
    """
    Display a warning in a pop up that informs
    about overwriting files
    """
    message_reply = QMessageBox.question(
        widget,
        title,
        message,
        QMessageBox.Yes | QMessageBox.Cancel,
    )
    if message_reply == QMessageBox.Yes:
        return True
    else:
        return False


# def overwrite_napari_roll(viewer):
#     """
#     Overwrite Napari _roll() function with something that makes more sense for a (mouse) brain
#     Goal: Cycle through views (e.g. asl -> lsa -> sal)
#     """
#     dims = get_dims_from_origins(ORIENTATIONS)
#
#     def _roll(self):
#         """Roll order of dimensions for display."""
#         dims_idx = dims.index(self.order)
#         next_dims = dims[(dims_idx + 1) % len(dims)]
#         self.order = next_dims
#
#     # Substitute Napari function
#     napari.components.dims.Dims._roll = _roll
