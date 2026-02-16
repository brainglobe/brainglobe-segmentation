from unittest.mock import patch

from brainglobe_segmentation.regions.analysis import (
    region_analysis,
    summarise_brain_regions,
)
from brainglobe_segmentation.regions.IO import (
    export_label_layers,
    save_label_layers,
)

### from segmentation_panels/regions.py


def test_add_new_region_button_show_info(
    segmentation_widget_with_data_atlas_space,
):
    """
    Directly call the add_new_region method and check show_info is triggered.
    """
    widget = segmentation_widget_with_data_atlas_space

    with patch(
        "brainglobe_segmentation.segmentation_panels.regions.show_info"
    ) as mock_show_info:
        with patch(
            "brainglobe_segmentation.segmentation_panels.regions.add_new_region_layer"
        ):
            # directly call the method the button triggers
            widget.region_seg.add_new_region()
            # check that show_info was called
            mock_show_info.assert_called_once_with("Adding a new region\n")


def test_add_region_from_existing_layer_button_show_info(
    segmentation_widget_with_data_atlas_space,
):
    """
    Directly call the add_region_from_existing_layer method
    and check show_info is triggered.
    """
    widget = segmentation_widget_with_data_atlas_space

    with (
        patch(
            "brainglobe_segmentation.segmentation_panels.regions.show_info"
        ) as mock_show_info,
        patch(
            "brainglobe_segmentation.segmentation_panels.regions.add_region_from_existing_layer"
        ),
        patch(
            "brainglobe_segmentation.segmentation_panels.regions.display_info"
        ),
    ):
        widget.region_seg.add_region_from_existing_layer()
        mock_show_info.assert_called_once_with(
            "Adding region from existing layer\n"
        )


def test_run_region_analysis_no_regions_show_info(segmentation_widget):
    widget = segmentation_widget

    with patch(
        "brainglobe_segmentation.segmentation_panels.regions.show_info"
    ) as mock_show_info:
        widget.region_seg.run_region_analysis()
        mock_show_info.assert_called_once_with("No regions found")


def test_run_region_analysis_cancel_show_info(
    segmentation_widget_with_data_atlas_space,
):
    widget = segmentation_widget_with_data_atlas_space

    with (
        patch(
            "brainglobe_segmentation.segmentation_panels.regions.show_info"
        ) as mock_show_info,
        patch(
            "brainglobe_segmentation.segmentation_panels.regions.display_warning",
            return_value=False,
        ),
    ):
        widget.region_seg.run_region_analysis()
        mock_show_info.assert_called_once_with(
            "Preventing analysis as user chose 'Cancel'"
        )


def test_run_region_analysis_show_info(
    segmentation_widget_with_data_atlas_space,
):
    widget = segmentation_widget_with_data_atlas_space

    with (
        patch(
            "brainglobe_segmentation.segmentation_panels.regions.show_info"
        ) as mock_show_info,
        patch(
            "brainglobe_segmentation.segmentation_panels.regions.display_warning",
            return_value=True,
        ),
    ):
        widget.region_seg.run_region_analysis()
        mock_show_info.assert_called_once_with("Running region analysis")


# from regions/IO.py


def test_save_label_layers_show_info(
    segmentation_widget_with_data_atlas_space,
):
    widget = segmentation_widget_with_data_atlas_space

    regions_directory = widget.paths.regions_directory
    label_layers = widget.label_layers

    with (
        patch(
            "brainglobe_segmentation.regions.IO.show_info"
        ) as mock_show_info,
        patch("brainglobe_segmentation.regions.IO.save_regions_to_file"),
    ):
        save_label_layers(regions_directory, label_layers)
        mock_show_info.assert_called_once_with(
            f"Saving regions to: {regions_directory}"
        )


def test_export_label_layers_show_info(
    segmentation_widget_with_data_atlas_space,
):
    widget = segmentation_widget_with_data_atlas_space

    regions_directory = widget.paths.regions_directory
    label_layers = widget.label_layers
    voxel_size = 50  # any value

    with (
        patch(
            "brainglobe_segmentation.regions.IO.show_info"
        ) as mock_show_info,
        patch("brainglobe_segmentation.regions.IO.export_regions_to_file"),
    ):
        export_label_layers(regions_directory, label_layers, voxel_size)
        mock_show_info.assert_called_once_with(
            f"Exporting regions to: {regions_directory}"
        )


### from regions/analysis.py


def test_region_analysis_show_info(
    segmentation_widget_with_data_atlas_space, tmp_path
):
    widget = segmentation_widget_with_data_atlas_space

    with (
        patch(
            "brainglobe_segmentation.regions.analysis.show_info"
        ) as mock_show_info,
        patch(
            "brainglobe_segmentation.regions.analysis.analyse_region_brain_areas"
        ),
        patch(
            "brainglobe_segmentation.regions.analysis.summarise_brain_regions"
        ),
    ):

        # call region_analysis with widget
        worker = region_analysis(
            label_layers=widget.label_layers,
            annotations_layer_image=widget.annotations_layer.data,
            atlas=widget.atlas,
            hemispheres=widget.hemispheres_data,
            regions_directory=tmp_path,
            output_csv_file=tmp_path / "summary.csv",
            volumes=True,
            summarise=True,
        )
        worker.run()

        mock_show_info.assert_any_call(
            "Calculating region volume distribution"
        )
        mock_show_info.assert_any_call(
            f"Saving summary volumes to: {tmp_path}"
        )
        mock_show_info.assert_any_call("Summarising regions")
        mock_show_info.assert_any_call("Finished!\n")


def test_summarise_brain_regions_no_regions_show_info(
    segmentation_widget_with_data_atlas_space, tmp_path
):
    widget = segmentation_widget_with_data_atlas_space

    # patch show_info and summarise_single_brain_region
    with (
        patch(
            "brainglobe_segmentation.regions.analysis.show_info"
        ) as mock_show_info,
        patch(
            "brainglobe_segmentation.regions.analysis.summarise_single_brain_region",
            return_value=None,
        ),
    ):

        # call summarise_brain_regions with widget label layers
        summarise_brain_regions(
            label_layers=widget.label_layers,
            filename=tmp_path / "summary.csv",
            atlas_resolution=widget.atlas.resolution,
        )

        mock_show_info.assert_called_once_with("No regions to summarise")
