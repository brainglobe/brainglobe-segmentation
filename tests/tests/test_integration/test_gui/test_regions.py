from filecmp import cmp
from pathlib import Path

import pandas as pd
import pytest

brainreg_dir = Path.cwd() / "tests" / "data" / "brainreg_output"
validate_regions_dir = (
    brainreg_dir / "manual_segmentation" / "standard_space" / "regions"
)


@pytest.fixture
def test_regions_dir(tmpdir):
    tmp_input_dir = tmpdir / "brainreg_output"
    test_regions_dir = (
        tmp_input_dir / "manual_segmentation" / "standard_space" / "regions"
    )
    return test_regions_dir


def test_region_widget_layer_numbers(
    segmentation_widget_with_data_atlas_space, test_regions_dir
):
    assert len(segmentation_widget_with_data_atlas_space.viewer.layers) == 4
    assert len(segmentation_widget_with_data_atlas_space.label_layers) == 1


def test_add_new_region(
    segmentation_widget_with_data_atlas_space, test_regions_dir
):
    segmentation_widget_with_data_atlas_space.region_seg.add_new_region()
    assert len(segmentation_widget_with_data_atlas_space.viewer.layers) == 5
    assert len(segmentation_widget_with_data_atlas_space.label_layers) == 2
    assert (
        segmentation_widget_with_data_atlas_space.label_layers[0].name
        == "test_region"
    )
    assert (
        segmentation_widget_with_data_atlas_space.label_layers[1].name
        == "region_1"
    )


def test_add_existing_region(
    segmentation_widget_with_data_atlas_space, test_regions_dir
):
    test_layer = segmentation_widget_with_data_atlas_space.viewer.add_labels(
        segmentation_widget_with_data_atlas_space.label_layers[0].data,
        name="test_region_2",
    )
    segmentation_widget_with_data_atlas_space.viewer.layers.selection.select_only(
        test_layer
    )
    segmentation_widget_with_data_atlas_space.region_seg.add_region_from_existing_layer(
        override=True
    )
    assert len(segmentation_widget_with_data_atlas_space.viewer.layers) == 5
    assert len(segmentation_widget_with_data_atlas_space.label_layers) == 2


def test_region_analysis(
    segmentation_widget_with_data_atlas_space, test_regions_dir
):
    segmentation_widget_with_data_atlas_space.region_seg.run_region_analysis(
        override=True
    )
    region_csv_validate = pd.read_csv(validate_regions_dir / "test_region.csv")
    region_csv_test = pd.read_csv(test_regions_dir / "test_region.csv")
    pd.testing.assert_frame_equal(region_csv_test, region_csv_validate)

    summary_csv_validate = pd.read_csv(validate_regions_dir / "summary.csv")
    summary_csv_test = pd.read_csv(test_regions_dir / "summary.csv")
    pd.testing.assert_frame_equal(summary_csv_test, summary_csv_validate)


def test_region_save(segmentation_widget_with_data_atlas_space):
    segmentation_widget_with_data_atlas_space.save(override=True)


def test_region_export(
    segmentation_widget_with_data_atlas_space, test_regions_dir
):
    segmentation_widget_with_data_atlas_space.export_to_brainrender(
        override=True
    )
    cmp(
        validate_regions_dir / "test_region.obj",
        test_regions_dir / "test_region.obj",
    )
