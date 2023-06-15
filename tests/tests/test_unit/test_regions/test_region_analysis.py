from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import tifffile
from napari.layers import Labels

from brainreg_segment.regions.analysis import (
    check_list_only_nones,
    summarise_brain_regions,
    summarise_single_brain_region,
)

region_image_path = Path(
    "tests/data/brainreg_output/manual_segmentation/"
    "sample_space/regions/region_0.tiff"
)
atlas_resolution = (50, 50, 50)
label_name = "test_label"

# We run regression tests against a previously known "correct run"
# that produced these values
previous_image_space_values = {
    "region": "test_label",
    "area": 17842.00000,
    "bbox-0": 134,
    "bbox-1": 34,
    "bbox-5": 65,
    "centroid-2": 44.284385158614505,
}

previous_world_space_values = {
    "region": "test_label",
    "volume_mm3": 2.23025,
    "axis_0_min_um": 6700.0,
    "axis_1_min_um": 1700.0,
    "axis_2_min_um": 1250.0,
    "axis_0_max_um": 7850.0,
    "axis_1_max_um": 3350.0,
    "axis_2_max_um": 3250.0,
    "axis_0_center_um": 7250.0,
    "axis_1_center_um": 2483.154915368232,
    "axis_2_center_um": 2214.219257930725,
}


@pytest.fixture
def region_image():
    return tifffile.imread(region_image_path)


@pytest.fixture
def labels_layer(region_image):
    labels = Labels(region_image, name=label_name)
    return labels


@pytest.fixture
def empty_labels_layer(region_image):
    labels = Labels(np.zeros_like(region_image))
    return labels


def test_check_list_only_ones():
    assert check_list_only_nones([None, None, None]) is True
    assert check_list_only_nones([None, 1, None]) is False
    assert check_list_only_nones([1, "two", 3]) is False


def test_summarise_single_brain_region(labels_layer):
    """
    Test the summary of a single segmented region.
    N.B. these results are in "image" space, not "world" space,
    hence different to the other tests
    """
    df = summarise_single_brain_region(labels_layer)
    assert df.shape == (1, 11)
    for key, value in previous_image_space_values.items():
        assert df[key].iloc[0] == value


def test_summarise_brain_regions_all_not_empty(
    labels_layer, empty_labels_layer, tmp_path
):
    """
    Test summarise_brain_regions() when all the regions
    (usually segmented by the user)
    contain at least one labelled voxel

    N.B. these results are in "world" space, not "space" space,
    hence different to the test of a single region
    """
    filename = tmp_path / "summary.csv"

    summarise_brain_regions(
        [labels_layer, labels_layer, labels_layer], filename, atlas_resolution
    )
    df = pd.read_csv(filename)
    assert df.shape == (3, 11)
    for key, value in previous_world_space_values.items():
        assert df[key].iloc[0] == value


def test_summarise_brain_regions_some_empty(
    labels_layer, empty_labels_layer, tmp_path
):
    """
    Test summarise_brain_regions() when some of the regions
    (usually segmented by the user)
    contain no voxels (i.e. are empty arrays), but
    others contain labelled voxels.

    N.B. these results are in "world" space, not "space" space,
    hence different to the test of a single region
    """

    filename = tmp_path / "summary.csv"
    summarise_brain_regions(
        [empty_labels_layer, empty_labels_layer, labels_layer],
        filename,
        atlas_resolution,
    )
    df = pd.read_csv(filename)
    assert df.shape == (1, 11)
    for key, value in previous_world_space_values.items():
        assert df[key].iloc[0] == value


def test_summarise_brain_regions_all_empty(
    labels_layer, empty_labels_layer, tmp_path
):
    """
    Test summarise_brain_regions() when all the regions
    (usually segmented by the user)
    contain no voxels (i.e. are empty arrays)
    """
    filename = tmp_path / "summary.csv"

    # check correct behaviour if all regions are empty
    assert (
        summarise_brain_regions(
            [empty_labels_layer, empty_labels_layer],
            filename,
            atlas_resolution,
        )
        is None
    )
