import shutil
from filecmp import cmp
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from brainreg_segment.segment import SegmentationWidget

brainreg_dir = Path.cwd() / "tests" / "data" / "brainreg_output"

ATLAS_NAME = "example_mouse_100um"


@pytest.fixture
def segmentation_widget(make_napari_viewer):
    """
    Create a viewer, add the curation widget, and return the widget.
    The viewer can be accessed using ``widget.viewer``.
    """
    viewer = make_napari_viewer()
    widget = SegmentationWidget(viewer)
    viewer.window.add_dock_widget(widget)
    return widget


def test_load_sample_space(segmentation_widget):
    segmentation_widget.standard_space = False
    segmentation_widget.plugin = "brainglobe-napari-io.brainreg_read_dir"
    segmentation_widget.directory = brainreg_dir
    segmentation_widget.load_brainreg_directory()
    check_loaded_layers(segmentation_widget, 7)


def test_load_standard_space(segmentation_widget):
    segmentation_widget.standard_space = True
    segmentation_widget.plugin = (
        "brainglobe-napari-io.brainreg_read_dir_standard_space"
    )
    segmentation_widget.directory = brainreg_dir
    segmentation_widget.load_brainreg_directory()
    check_loaded_layers(segmentation_widget, 4)


def check_loaded_layers(widget, num_layers):
    assert len(widget.viewer.layers) == num_layers
    assert widget.base_layer.name == "Registered image"
    assert widget.atlas.atlas_name == "allen_mouse_50um"
    assert widget.metadata["orientation"] == "psl"
    assert widget.atlas_layer.name == widget.atlas.atlas_name


def test_load_atlas(segmentation_widget, tmpdir):
    segmentation_widget.directory = tmpdir
    segmentation_widget.current_atlas_name = ATLAS_NAME
    segmentation_widget.load_atlas()
    assert len(segmentation_widget.viewer.layers) == 2
    assert segmentation_widget.base_layer.name == "Reference"
    assert segmentation_widget.atlas.atlas_name == ATLAS_NAME
    assert (
        segmentation_widget.atlas_layer.name
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


def test_tracks(segmentation_widget, tmpdir, rtol=1e-10):
    tmp_input_dir = tmpdir / "brainreg_output"
    test_tracks_dir = (
        tmp_input_dir / "manual_segmentation" / "standard_space" / "tracks"
    )
    validate_tracks_dir = (
        brainreg_dir / "manual_segmentation" / "standard_space" / "tracks"
    )
    shutil.copytree(brainreg_dir, tmp_input_dir)
    segmentation_widget.standard_space = True
    segmentation_widget.plugin = (
        "brainglobe-napari-io.brainreg_read_dir_standard_space"
    )
    segmentation_widget.directory = Path(tmp_input_dir)
    segmentation_widget.load_brainreg_directory()

    assert len(segmentation_widget.viewer.layers) == 4
    assert len(segmentation_widget.track_layers) == 1
    segmentation_widget.track_seg.add_track()
    assert len(segmentation_widget.viewer.layers) == 5
    assert len(segmentation_widget.track_layers) == 2
    assert segmentation_widget.track_layers[0].name == "test_track"
    assert segmentation_widget.track_layers[1].name == "track_1"
    assert len(segmentation_widget.track_layers[0].data) == 6

    # analysis
    segmentation_widget.track_seg.run_track_analysis(override=True)
    regions_validate = pd.read_csv(validate_tracks_dir / "test_track.csv")
    regions_test = pd.read_csv(test_tracks_dir / "test_track.csv")
    pd.testing.assert_frame_equal(regions_validate, regions_test)

    # saving
    segmentation_widget.save(override=True)
    points_validate = pd.read_hdf(validate_tracks_dir / "test_track.points")
    points_test = pd.read_hdf(test_tracks_dir / "test_track.points")
    np.testing.assert_allclose(points_validate, points_test, rtol=rtol)

    # export
    segmentation_widget.export_to_brainrender(override=True)
    spline_validate = pd.read_hdf(validate_tracks_dir / "test_track.h5")
    spline_test = pd.read_hdf(test_tracks_dir / "test_track.h5")
    pd.testing.assert_frame_equal(spline_test, spline_validate)

    # surface points
    segmentation_widget.track_seg.add_surface_points()
    assert len(segmentation_widget.track_layers[0].data) == 7


def test_regions(segmentation_widget, tmpdir, rtol=1e-10):
    tmp_input_dir = tmpdir / "brainreg_output"
    test_regions_dir = (
        tmp_input_dir / "manual_segmentation" / "standard_space" / "regions"
    )
    validate_regions_dir = (
        brainreg_dir / "manual_segmentation" / "standard_space" / "regions"
    )
    shutil.copytree(brainreg_dir, tmp_input_dir)
    segmentation_widget.standard_space = True
    segmentation_widget.plugin = (
        "brainglobe-napari-io.brainreg_read_dir_standard_space"
    )
    segmentation_widget.directory = Path(tmp_input_dir)
    segmentation_widget.load_brainreg_directory()

    assert len(segmentation_widget.viewer.layers) == 4
    assert len(segmentation_widget.label_layers) == 1
    segmentation_widget.region_seg.add_region()
    assert len(segmentation_widget.viewer.layers) == 5
    assert len(segmentation_widget.label_layers) == 2
    assert segmentation_widget.label_layers[0].name == "test_region"
    assert segmentation_widget.label_layers[1].name == "region_1"

    # analysis
    segmentation_widget.region_seg.run_region_analysis(override=True)
    region_csv_validate = pd.read_csv(validate_regions_dir / "test_region.csv")
    region_csv_test = pd.read_csv(test_regions_dir / "test_region.csv")
    pd.testing.assert_frame_equal(region_csv_test, region_csv_validate)

    summary_csv_validate = pd.read_csv(validate_regions_dir / "summary.csv")
    summary_csv_test = pd.read_csv(test_regions_dir / "summary.csv")
    pd.testing.assert_frame_equal(summary_csv_test, summary_csv_validate)

    # saving
    segmentation_widget.save(override=True)

    # export
    segmentation_widget.export_to_brainrender(override=True)
    cmp(
        validate_regions_dir / "test_region.obj",
        test_regions_dir / "test_region.obj",
    )
