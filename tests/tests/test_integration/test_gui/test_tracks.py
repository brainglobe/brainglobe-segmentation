from pathlib import Path

import numpy as np
import pandas as pd
import pytest

brainreg_dir = Path.cwd() / "tests" / "data" / "brainreg_output"
validate_tracks_dir = (
    brainreg_dir / "manual_segmentation" / "standard_space" / "tracks"
)


@pytest.fixture
def test_tracks_dir(tmpdir):
    tmp_input_dir = tmpdir / "brainreg_output"
    test_tracks_dir = (
        tmp_input_dir / "manual_segmentation" / "standard_space" / "tracks"
    )
    return test_tracks_dir


def test_track_widget_layer_numbers(
    segmentation_widget_with_data_atlas_space, test_tracks_dir
):
    assert len(segmentation_widget_with_data_atlas_space.viewer.layers) == 4
    assert len(segmentation_widget_with_data_atlas_space.track_layers) == 1


def test_add_new_track(
    segmentation_widget_with_data_atlas_space, test_tracks_dir
):
    segmentation_widget_with_data_atlas_space.track_seg.add_track()
    assert len(segmentation_widget_with_data_atlas_space.viewer.layers) == 5
    assert len(segmentation_widget_with_data_atlas_space.track_layers) == 2
    assert (
        segmentation_widget_with_data_atlas_space.track_layers[0].name
        == "test_track"
    )
    assert (
        segmentation_widget_with_data_atlas_space.track_layers[1].name
        == "track_1"
    )
    assert (
        len(segmentation_widget_with_data_atlas_space.track_layers[0].data)
        == 6
    )


def test_add_existing_track(
    segmentation_widget_with_data_atlas_space, test_tracks_dir
):
    segmentation_widget = segmentation_widget_with_data_atlas_space

    # importing existing track
    points = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2], [3, 3, 3]])
    test_layer = segmentation_widget.viewer.add_points(
        points, name="test_track2"
    )
    segmentation_widget.viewer.layers.selection.select_only(test_layer)
    segmentation_widget.track_seg.add_track_from_existing_layer(override=True)
    assert len(segmentation_widget.viewer.layers) == 5
    assert len(segmentation_widget.track_layers) == 2


def test_add_surface_point(
    segmentation_widget_with_data_atlas_space, test_tracks_dir
):
    segmentation_widget_with_data_atlas_space.track_seg.add_surface_points()
    assert (
        len(segmentation_widget_with_data_atlas_space.track_layers[0].data)
        == 7
    )


def test_track_analysis_without_save(
    segmentation_widget_with_data_atlas_space, test_tracks_dir
):
    segmentation_widget_with_data_atlas_space.track_seg.save_checkbox.setChecked(
        False
    )

    segmentation_widget_with_data_atlas_space.track_seg.run_track_analysis(
        override=True
    )
    # check saving didn't happen
    assert (test_tracks_dir / "test_track.points").exists() is False

    check_analysis(test_tracks_dir, validate_tracks_dir)


def test_track_analysis_with_save(
    segmentation_widget_with_data_atlas_space, test_tracks_dir, rtol=1e-10
):
    segmentation_widget_with_data_atlas_space.track_seg.save_checkbox.setChecked(
        True
    )
    segmentation_widget_with_data_atlas_space.track_seg.run_track_analysis(
        override=True
    )

    check_analysis(test_tracks_dir, validate_tracks_dir)
    check_saving(test_tracks_dir, validate_tracks_dir, rtol)


def test_track_save(
    segmentation_widget_with_data_atlas_space, test_tracks_dir, rtol=1e-10
):
    check_saving(test_tracks_dir, validate_tracks_dir, rtol)


def test_track_export(
    segmentation_widget_with_data_atlas_space, test_tracks_dir
):
    segmentation_widget_with_data_atlas_space.export_to_brainrender(
        override=True
    )
    spline_validate = pd.read_hdf(validate_tracks_dir / "test_track.h5")
    spline_test = pd.read_hdf(test_tracks_dir / "test_track.h5")
    pd.testing.assert_frame_equal(spline_test, spline_validate)


def check_analysis(test_tracks_dir, validate_tracks_dir):
    regions_validate = pd.read_csv(validate_tracks_dir / "test_track.csv")
    regions_test = pd.read_csv(test_tracks_dir / "test_track.csv")
    pd.testing.assert_frame_equal(regions_validate, regions_test)


def check_saving(test_tracks_dir, validate_tracks_dir, rtol):
    points_validate = pd.read_hdf(validate_tracks_dir / "test_track.points")
    points_test = pd.read_hdf(test_tracks_dir / "test_track.points")
    np.testing.assert_allclose(points_validate, points_test, rtol=rtol)
