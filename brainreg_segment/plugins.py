from napari_plugin_engine import napari_hook_implementation
from brainreg_segment.segment import SegmentationWidget
from brainreg_segment.measurement import measurement
from brainreg_segment.measurement.random_layers import (
    generate_random_points_2d_layer,
    generate_random_points_3d_layer,
)


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return [
        (SegmentationWidget, {"name": "Manual segmentation"}),
        (measurement.analyze_points_layer, {"name": "Analyze points layer"}),
    ]


@napari_hook_implementation
def napari_provide_sample_data():
    return {
        "random 3d points": generate_random_points_3d_layer,
        "random 2d points": generate_random_points_2d_layer,
    }
