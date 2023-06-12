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


def test_summarise_brain_regions(labels_layer, empty_labels_layer, tmp_path):
    filename = tmp_path / "summary.csv"

    # check correct behaviour if all regions are not empty

    summarise_brain_regions(
        [labels_layer, labels_layer, labels_layer], filename, atlas_resolution
    )
    df = pd.read_csv(filename)
    assert df.shape == (3, 11)
    assert df["region"].iloc[0] == label_name
    assert np.isclose(df["volume_mm3"].iloc[0], 2.23025)
    assert np.isclose(df["axis_1_center_um"].iloc[0], 2483.15492)

    # check correct behaviour if all regions are empty
    assert (
        summarise_brain_regions(
            [empty_labels_layer, empty_labels_layer],
            filename,
            atlas_resolution,
        )
        is None
    )

    # check correct behaviour if some regions are empty
    filename = tmp_path / "summary2.csv"
    summarise_brain_regions(
        [empty_labels_layer, empty_labels_layer, labels_layer],
        filename,
        atlas_resolution,
    )
    df = pd.read_csv(filename)
    assert df.shape == (1, 11)
    assert df["region"].iloc[0] == label_name
    assert np.isclose(df["axis_0_max_um"].iloc[0], 7850)
    assert np.isclose(df["axis_2_center_um"].iloc[0], 2214.21926)


def test_summarise_single_brain_region(labels_layer):
    df = summarise_single_brain_region(labels_layer)
    assert df.shape == (1, 11)
    assert df["region"].iloc[0] == label_name
    assert df["area"].iloc[0] == 17842.0
    assert np.isclose(df["centroid-2"].iloc[0], 44.28439)
