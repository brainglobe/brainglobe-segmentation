from napari_plugin_engine import napari_hook_implementation
from brainreg_segment.segment import SegmentationWidget


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return SegmentationWidget, {"name": "Manual segmentation"}
