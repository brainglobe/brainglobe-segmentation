from pathlib import Path

import numpy as np

brainreg_dir = Path.cwd() / "tests" / "data" / "brainreg_output"

ATLAS_NAME = "example_mouse_100um"


def test_load_sample_space(segmentation_widget):
    segmentation_widget.standard_space = False
    segmentation_widget.plugin = "brainglobe-napari-io.brainreg_read_dir"
    segmentation_widget.directory = brainreg_dir
    segmentation_widget.load_brainreg_directory()
    check_loaded_layers(segmentation_widget, 7)
    check_not_editable(segmentation_widget, standard_space=False)


def test_load_standard_space(segmentation_widget):
    segmentation_widget.standard_space = True
    segmentation_widget.plugin = (
        "brainglobe-napari-io.brainreg_read_dir_standard_space"
    )
    segmentation_widget.directory = brainreg_dir
    segmentation_widget.load_brainreg_directory()
    check_loaded_layers(segmentation_widget, 4)
    check_not_editable(segmentation_widget, standard_space=True)


def test_layer_deletion(segmentation_widget):
    """
    Check that remove_layers() doesn't remove any layers that were present
    before brainreg-segment added layers
    """
    assert len(segmentation_widget.viewer.layers) == 0
    segmentation_widget.viewer.add_points(np.array([[1, 1], [2, 2]]))
    assert len(segmentation_widget.viewer.layers) == 1
    segmentation_widget.standard_space = False
    segmentation_widget.plugin = "brainglobe-napari-io.brainreg_read_dir"
    segmentation_widget.directory = brainreg_dir
    segmentation_widget.load_brainreg_directory()
    # Brainreg should load 7 new layers
    check_loaded_layers(segmentation_widget, 8)


def check_loaded_layers(widget, num_layers):
    assert len(widget.viewer.layers) == num_layers
    assert widget.base_layer.name == "Registered image"
    assert widget.atlas.atlas_name == "allen_mouse_50um"
    assert widget.metadata["orientation"] == "psl"
    assert widget.annotations_layer.name == widget.atlas.atlas_name


def check_not_editable(widget, standard_space=False):
    assert widget.base_layer.editable is False
    assert widget.annotations_layer.editable is False
    if not standard_space:
        assert widget.viewer.layers["Hemispheres"].editable is False


def test_load_atlas(segmentation_widget, tmp_path):
    segmentation_widget.directory = tmp_path
    segmentation_widget.current_atlas_name = ATLAS_NAME
    segmentation_widget.load_atlas()
    assert len(segmentation_widget.viewer.layers) == 2
    assert segmentation_widget.base_layer.name == "Reference"
    assert segmentation_widget.atlas.atlas_name == ATLAS_NAME
    assert (
        segmentation_widget.annotations_layer.name
        == segmentation_widget.atlas.atlas_name
    )


def test_general(segmentation_widget):
    segmentation_widget.standard_space = True
    segmentation_widget.plugin = (
        "brainglobe-napari-io.brainreg_read_dir_standard_space"
    )
    segmentation_widget.directory = brainreg_dir
    segmentation_widget.load_brainreg_directory()
    assert segmentation_widget.mean_voxel_size == 50
    check_defaults(segmentation_widget)
    check_paths(segmentation_widget)


def check_defaults(widget):
    assert widget.track_seg.point_size == int(100 / widget.mean_voxel_size)
    assert widget.track_seg.spline_size == int(50 / widget.mean_voxel_size)
    assert widget.track_seg.track_file_extension == ".points"
    assert widget.region_seg.image_file_extension == ".tiff"
    assert widget.region_seg.num_colors == 10
    assert widget.region_seg.brush_size == int(250 / widget.mean_voxel_size)
    assert widget.track_seg.spline_points_default == 1000
    assert widget.track_seg.spline_smoothing_default == 0.1
    assert widget.track_seg.fit_degree_default == 3
    assert widget.track_seg.summarise_track_default is True
    assert widget.region_seg.calculate_volumes_default is True
    assert widget.region_seg.summarise_volumes_default is True
    assert widget.boundaries_string == "Boundaries"


def check_paths(widget):
    assert widget.paths.main_directory == brainreg_dir / "manual_segmentation"

    assert (
        widget.paths.segmentation_directory
        == brainreg_dir / "manual_segmentation" / "standard_space"
    )

    assert (
        widget.paths.regions_directory
        == brainreg_dir / "manual_segmentation" / "standard_space" / "regions"
    )

    assert (
        widget.paths.region_summary_csv
        == brainreg_dir
        / "manual_segmentation"
        / "standard_space"
        / "regions"
        / "summary.csv"
    )
    assert (
        widget.paths.tracks_directory
        == brainreg_dir / "manual_segmentation" / "standard_space" / "tracks"
    )
