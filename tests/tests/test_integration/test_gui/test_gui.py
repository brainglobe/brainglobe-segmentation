import shutil
from pathlib import Path
from brainreg_segment.segment import SegmentationWidget
import pandas as pd

brainreg_dir = Path.cwd() / "tests" / "data" / "brainreg_output"

ATLAS_NAME = "example_mouse_100um"


def test_load_sample_space(make_test_viewer):
    viewer = make_test_viewer()
    widget = SegmentationWidget(viewer)
    viewer.window.add_dock_widget(widget, name="General", area="right")
    widget.standard_space = False
    widget.plugin = "brainreg"
    widget.directory = brainreg_dir
    widget.load_brainreg_directory()
    check_loaded_layers(widget, 6)


def test_load_standard_space(make_test_viewer):
    viewer = make_test_viewer()
    widget = SegmentationWidget(viewer)
    viewer.window.add_dock_widget(widget, name="General", area="right")
    widget.standard_space = True
    widget.plugin = "brainreg_standard"
    widget.directory = brainreg_dir
    widget.load_brainreg_directory()
    check_loaded_layers(widget, 4)


def test_load_atlas(tmpdir, make_test_viewer):
    viewer = make_test_viewer()
    widget = SegmentationWidget(viewer)
    viewer.window.add_dock_widget(widget, name="General", area="right")
    widget.directory = tmpdir
    widget.add_atlas_menu()
    widget.load_atlas(ATLAS_NAME)
    assert len(widget.viewer.layers) == 2
    assert widget.base_layer.name == "Reference"
    assert widget.atlas.atlas_name == ATLAS_NAME
    assert widget.atlas_layer.name == widget.atlas.atlas_name


def test_general(make_test_viewer):
    viewer = make_test_viewer()
    widget = SegmentationWidget(viewer)
    viewer.window.add_dock_widget(widget, name="General", area="right")
    widget.standard_space = True
    widget.plugin = "brainreg_standard"
    widget.directory = brainreg_dir
    widget.load_brainreg_directory()
    assert widget.mean_voxel_size == 50
    check_defaults(widget)
    check_paths(widget)


def test_tracks(tmpdir, make_test_viewer):
    tmp_input_dir = tmpdir / "brainreg_output"
    shutil.copytree(brainreg_dir, tmp_input_dir)
    viewer = make_test_viewer()
    widget = SegmentationWidget(viewer)
    viewer.window.add_dock_widget(widget, name="General", area="right")
    widget.standard_space = True
    widget.plugin = "brainreg_standard"
    widget.directory = tmp_input_dir
    widget.load_brainreg_directory()

    assert len(widget.viewer.layers) == 4
    assert len(widget.track_layers) == 1
    widget.add_track()
    assert len(widget.viewer.layers) == 5
    assert len(widget.track_layers) == 2
    assert widget.track_layers[0].name == "test_track"
    assert widget.track_layers[1].name == "track_1"
    assert len(widget.track_layers[0].data) == 5

    widget.run_track_analysis()

    regions_validate = pd.read_csv(
        brainreg_dir
        / "manual_segmentation"
        / "standard_space"
        / "tracks"
        / "test_track.csv"
    )
    regions_test = pd.read_csv(
        tmp_input_dir
        / "manual_segmentation"
        / "standard_space"
        / "tracks"
        / "test_track.csv"
    )

    pd.testing.assert_frame_equal(regions_test, regions_validate)

    widget.add_surface_points()
    assert len(widget.track_layers[0].data) == 6


def test_regions(tmpdir, make_test_viewer):
    tmp_input_dir = tmpdir / "brainreg_output"
    shutil.copytree(brainreg_dir, tmp_input_dir)
    viewer = make_test_viewer()
    widget = SegmentationWidget(viewer)
    viewer.window.add_dock_widget(widget, name="General", area="right")
    widget.standard_space = True
    widget.plugin = "brainreg_standard"
    widget.directory = tmp_input_dir
    widget.load_brainreg_directory()

    assert len(widget.viewer.layers) == 4
    assert len(widget.label_layers) == 1
    widget.add_new_region()
    assert len(widget.viewer.layers) == 5
    assert len(widget.label_layers) == 2
    assert widget.label_layers[0].name == "test_region"
    assert widget.label_layers[1].name == "region_1"


def check_loaded_layers(widget, num_layers):
    assert len(widget.viewer.layers) == num_layers
    assert widget.base_layer.name == "Registered image"
    assert widget.atlas.atlas_name == "allen_mouse_50um"
    assert widget.metadata["orientation"] == "psl"
    assert widget.atlas_layer.name == widget.atlas.atlas_name


def check_defaults(widget):
    assert widget.point_size == int(100 / widget.mean_voxel_size)
    assert widget.spline_size == int(50 / widget.mean_voxel_size)
    assert widget.track_file_extension == ".points"
    assert widget.image_file_extension == ".tiff"
    assert widget.num_colors == 10
    assert widget.brush_size == int(250 / widget.mean_voxel_size)
    assert widget.spline_points_default == 1000
    assert widget.spline_smoothing_default == 0.1
    assert widget.fit_degree_default == 3
    assert widget.summarise_track_default is True
    assert widget.add_surface_point_default is False
    assert widget.calculate_volumes_default is True
    assert widget.summarise_volumes_default is True
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
