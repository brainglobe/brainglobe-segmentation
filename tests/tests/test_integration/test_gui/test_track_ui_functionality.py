from pathlib import Path
from time import sleep

import numpy as np
import pandas as pd
import pytest

brainreg_dir = Path.cwd() / "tests" / "data" / "brainreg_output"
validate_tracks_dir = brainreg_dir / "segmentation" / "atlas_space" / "tracks"


@pytest.fixture
def test_tracks_dir(tmp_path):
    tmp_input_dir = tmp_path / "brainreg_output"
    test_tracks_dir = tmp_input_dir / "segmentation" / "atlas_space" / "tracks"
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
    segmentation_widget_with_data_atlas_space.track_seg.run_track_analysis(
        override=True
    )
    # check saving didn't happen (default)
    test_saved_track = Path(test_tracks_dir / "test_track.points")
    assert test_saved_track.exists() is False

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
    segmentation_widget_with_data_atlas_space.save(override=True)

    # ensure data is saved before it is loaded again
    sleep(8)
    check_saving(test_tracks_dir, validate_tracks_dir, rtol)


def test_track_export(
    segmentation_widget_with_data_atlas_space, test_tracks_dir
):
    segmentation_widget_with_data_atlas_space.track_seg.run_track_analysis(
        override=True
    )
    segmentation_widget_with_data_atlas_space.export_to_brainrender(
        override=True
    )

    # ensure data is saved before it is loaded again
    sleep(8)
    spline_validate = np.load(validate_tracks_dir / "test_track.npy")
    spline_test = np.load(test_tracks_dir / "test_track.npy")
    np.testing.assert_allclose(spline_validate, spline_test)


def compare_dataframes(df1, df2, threshold=0.9):
    """
    Function to check how many entries are the same,
    not how similar they are.

    Required due to slight differences between operating
    systems & architectures
    """
    if df1.shape != df2.shape:
        raise ValueError("DataFrames are not the same shape.")

    total_entries = df1.shape[0] * df1.shape[1]
    matching_entries = (df1 == df2).sum().sum()
    similarity = matching_entries / total_entries
    return similarity >= threshold


def check_analysis(test_tracks_dir, validate_tracks_dir):
    regions_validate = pd.read_csv(validate_tracks_dir / "test_track.csv")
    regions_test = pd.read_csv(test_tracks_dir / "test_track.csv")
    # Threshold of 0.9 is not ideal but sight differences in the analysis
    # can have big effects on the final result (e.g. assigning to
    # neighbouring anatomical areas
    assert compare_dataframes(regions_validate, regions_test)


def check_saving(test_tracks_dir, validate_tracks_dir, rtol):
    points_validate = pd.read_hdf(validate_tracks_dir / "test_track.points")
    points_test = pd.read_hdf(test_tracks_dir / "test_track.points")
    np.testing.assert_allclose(points_validate, points_test, rtol=rtol)
