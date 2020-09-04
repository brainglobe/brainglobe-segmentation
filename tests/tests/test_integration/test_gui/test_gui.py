import shutil

# import tifffile

import numpy as np
import pandas as pd

from pathlib import Path
from filecmp import cmp
from brainreg_segment.segment import SegmentationWidget

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
    widget.current_atlas_name = ATLAS_NAME
    widget.load_atlas()
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


def test_tracks(tmpdir, make_test_viewer, rtol=1e-10):
    tmp_input_dir = tmpdir / "brainreg_output"
    test_tracks_dir = (
        tmp_input_dir / "manual_segmentation" / "standard_space" / "tracks"
    )
    validate_tracks_dir = (
        brainreg_dir / "manual_segmentation" / "standard_space" / "tracks"
    )
    shutil.copytree(brainreg_dir, tmp_input_dir)
    viewer = make_test_viewer()
    widget = SegmentationWidget(viewer)
    viewer.window.add_dock_widget(widget, name="General", area="right")
    widget.standard_space = True
    widget.plugin = "brainreg_standard"
    widget.directory = Path(tmp_input_dir)
    widget.load_brainreg_directory()

    assert len(widget.viewer.layers) == 4
    assert len(widget.track_layers) == 1
    widget.track_seg.add_track()
    assert len(widget.viewer.layers) == 5
    assert len(widget.track_layers) == 2
    assert widget.track_layers[0].name == "test_track"
    assert widget.track_layers[1].name == "track_1"
    assert len(widget.track_layers[0].data) == 6

    # analysis
    widget.track_seg.run_track_analysis()
    regions_validate = pd.read_csv(validate_tracks_dir / "test_track.csv")
    regions_test = pd.read_csv(test_tracks_dir / "test_track.csv")
    pd.testing.assert_frame_equal(regions_validate, regions_test)

    # saving
    widget.save()
    points_validate = pd.read_hdf(validate_tracks_dir / "test_track.points")
    points_test = pd.read_hdf(test_tracks_dir / "test_track.points")
    np.testing.assert_allclose(points_validate, points_test, rtol=rtol)

    # export
    widget.export_to_brainrender()
    spline_validate = pd.read_hdf(validate_tracks_dir / "test_track.h5")
    spline_test = pd.read_hdf(test_tracks_dir / "test_track.h5")
    pd.testing.assert_frame_equal(spline_test, spline_validate)

    # surface points
    widget.track_seg.add_surface_points()
    assert len(widget.track_layers[0].data) == 7


def test_regions(tmpdir, make_test_viewer, rtol=1e-10):
    tmp_input_dir = tmpdir / "brainreg_output"
    test_regions_dir = (
        tmp_input_dir / "manual_segmentation" / "standard_space" / "regions"
    )
    validate_regions_dir = (
        brainreg_dir / "manual_segmentation" / "standard_space" / "regions"
    )
    shutil.copytree(brainreg_dir, tmp_input_dir)
    viewer = make_test_viewer()
    widget = SegmentationWidget(viewer)
    viewer.window.add_dock_widget(widget, name="General", area="right")
    widget.standard_space = True
    widget.plugin = "brainreg_standard"
    widget.directory = Path(tmp_input_dir)
    widget.load_brainreg_directory()

    assert len(widget.viewer.layers) == 4
    assert len(widget.label_layers) == 1
    widget.region_seg.add_region()
    assert len(widget.viewer.layers) == 5
    assert len(widget.label_layers) == 2
    assert widget.label_layers[0].name == "test_region"
    assert widget.label_layers[1].name == "region_1"

    # analysis
    widget.region_seg.run_region_analysis()
    region_csv_validate = pd.read_csv(validate_regions_dir / "test_region.csv")
    region_csv_test = pd.read_csv(test_regions_dir / "test_region.csv")
    pd.testing.assert_frame_equal(region_csv_test, region_csv_validate)

    summary_csv_validate = pd.read_csv(validate_regions_dir / "summary.csv")
    summary_csv_test = pd.read_csv(test_regions_dir / "summary.csv")
    pd.testing.assert_frame_equal(summary_csv_test, summary_csv_validate)

    # saving
    widget.save()

    # image_validate = tifffile.imread(validate_regions_dir / "test_region.tiff")
    # image_test = tifffile.imread(test_regions_dir / "test_region.tiff")
    # np.testing.assert_allclose(image_validate, image_test, rtol=rtol)

    # export
    widget.export_to_brainrender()
    cmp(
        validate_regions_dir / "test_region.obj",
        test_regions_dir / "test_region.obj",
    )


def check_loaded_layers(widget, num_layers):
    assert len(widget.viewer.layers) == num_layers
    assert widget.base_layer.name == "Registered image"
    assert widget.atlas.atlas_name == "allen_mouse_50um"
    assert widget.metadata["orientation"] == "psl"
    assert widget.atlas_layer.name == widget.atlas.atlas_name


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
