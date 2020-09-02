# Small layout utils
from napari.viewer import Viewer


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
