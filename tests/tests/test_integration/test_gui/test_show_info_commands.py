from unittest.mock import patch

import numpy as np
import pytest

from brainglobe_segmentation.regions.analysis import (
    analyse_region_brain_areas,
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
            widget.region_seg.add_new_region()
            mock_show_info.assert_called_once_with("Adding a new region")


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
            "Adding region from existing layer"
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


@pytest.mark.parametrize(
    "volumes,summarise,output_csv_file,expected_calls",
    [
        (
            True,
            True,
            "summary.csv",
            [
                "Calculating region volume distribution",
                "Saving summary volumes to:",
                "Summarising regions",
                "Finished!",
            ],
        ),
        (
            True,
            False,
            "summary.csv",
            [
                "Calculating region volume distribution",
                "Saving summary volumes to:",
                "Finished!",
            ],
        ),
        (
            False,
            True,
            "summary.csv",
            [
                "Summarising regions",
                "Finished!",
            ],
        ),
        (
            False,
            False,
            "summary.csv",
            [
                "Finished!",
            ],
        ),
        (
            False,
            True,
            None,
            [
                "Finished!",
            ],
        ),
    ],
)
def test_region_analysis_show_info(
    segmentation_widget_with_data_atlas_space,
    tmp_path,
    volumes,
    summarise,
    output_csv_file,
    expected_calls,
):
    widget = segmentation_widget_with_data_atlas_space

    if output_csv_file is not None:
        output_csv_file = tmp_path / output_csv_file

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
        worker = region_analysis(
            label_layers=widget.label_layers,
            annotations_layer_image=widget.annotations_layer.data,
            atlas=widget.atlas,
            hemispheres=widget.hemispheres_data,
            regions_directory=tmp_path,
            output_csv_file=output_csv_file,
            volumes=volumes,
            summarise=summarise,
        )
        worker.run()

        for expected_call in expected_calls:
            if expected_call == "Saving summary volumes to:":
                assert any(
                    call.args[0].startswith(expected_call)
                    for call in mock_show_info.call_args_list
                )
            else:
                mock_show_info.assert_any_call(expected_call)


def test_summarise_brain_regions_no_regions_show_info(
    segmentation_widget_with_data_atlas_space, tmp_path
):
    widget = segmentation_widget_with_data_atlas_space
    with (
        patch(
            "brainglobe_segmentation.regions.analysis.show_info"
        ) as mock_show_info,
        patch(
            "brainglobe_segmentation.regions.analysis.summarise_single_brain_region",
            return_value=None,
        ),
    ):

        summarise_brain_regions(
            label_layers=widget.label_layers,
            filename=tmp_path / "summary.csv",
            atlas_resolution=widget.atlas.resolution,
        )

        mock_show_info.assert_called_once_with("No regions to summarise")


def test_analyse_region_brain_areas_show_info_on_missing_structure(
    segmentation_widget_with_data_atlas_space, tmp_path
):
    widget = segmentation_widget_with_data_atlas_space
    label_layer = widget.label_layers[0]

    with (
        patch(
            "brainglobe_segmentation.regions.analysis.show_info"
        ) as mock_show_info,
        patch(
            "brainglobe_segmentation.regions.analysis.add_structure_volume_to_df",
            side_effect=KeyError,
        ),
    ):

        analyse_region_brain_areas(
            label_layer=label_layer,
            annotations_layer_image=widget.annotations_layer.data,
            hemispheres=widget.hemispheres_data,
            destination_directory=tmp_path,
            atlas=widget.atlas,
        )

        mock_show_info.assert_called()


### from segmentations_panels/tracks


def test_add_track_show_info(segmentation_widget_with_data_atlas_space):
    widget = segmentation_widget_with_data_atlas_space

    with (
        patch(
            "brainglobe_segmentation.segmentation_panels.tracks.show_info"
        ) as mock_show_info,
        patch(
            "brainglobe_segmentation.segmentation_panels.tracks.add_new_track_layer"
        ),
    ):
        widget.track_seg.add_track()

        mock_show_info.assert_called_once_with("Adding a new track")


def test_add_track_from_existing_layer_show_info(
    segmentation_widget_with_data_atlas_space,
):
    widget = segmentation_widget_with_data_atlas_space

    with (
        patch(
            "brainglobe_segmentation.segmentation_panels.tracks.show_info"
        ) as mock_show_info,
        patch(
            "brainglobe_segmentation.segmentation_panels.tracks.add_track_from_existing_layer"
        ),
        patch(
            "brainglobe_segmentation.segmentation_panels.tracks.display_info"
        ),
    ):

        widget.track_seg.add_track_from_existing_layer()

        mock_show_info.assert_called_once_with(
            "Adding track from existing layer"
        )


def test_add_surface_points_no_tracks_show_info(segmentation_widget):
    widget = segmentation_widget

    with patch(
        "brainglobe_segmentation.segmentation_panels.tracks.show_info"
    ) as mock_show_info:
        widget.track_seg.add_surface_points()

        mock_show_info.assert_called_once_with("No tracks found.")


def test_add_surface_points_show_info(
    segmentation_widget_with_data_atlas_space,
):
    widget = segmentation_widget_with_data_atlas_space

    with patch(
        "brainglobe_segmentation.segmentation_panels.tracks.show_info"
    ) as mock_show_info:
        widget.track_seg.add_surface_points()

        mock_show_info.assert_any_call(
            "Adding surface points (this may take a while)"
        )
        mock_show_info.assert_any_call("Finished!")


def test_add_surface_points_empty_track_show_info(
    segmentation_widget_with_data_atlas_space,
):
    widget = segmentation_widget_with_data_atlas_space
    track_layer = widget.track_seg.parent.track_layers[0]

    with patch(
        "brainglobe_segmentation.segmentation_panels.tracks.show_info"
    ) as mock_show_info:
        track_layer.data = np.empty((0, 3))

        widget.track_seg.add_surface_points()

        mock_show_info.assert_any_call(
            "Adding surface points (this may take a while)"
        )
        mock_show_info.assert_any_call(
            f"{track_layer.name} does not appear to hold any data"
        )


def test_run_track_analysis_no_tracks_show_info(segmentation_widget):
    widget = segmentation_widget

    with patch(
        "brainglobe_segmentation.segmentation_panels.tracks.show_info"
    ) as mock_show_info:
        widget.track_seg.run_track_analysis()

        mock_show_info.assert_called_once_with("No tracks found.")


def test_run_track_analysis_cancel_show_info(
    segmentation_widget_with_data_atlas_space,
):
    widget = segmentation_widget_with_data_atlas_space

    with (
        patch(
            "brainglobe_segmentation.segmentation_panels.tracks.show_info"
        ) as mock_show_info,
        patch(
            "brainglobe_segmentation.segmentation_panels.tracks.display_warning",
            return_value=False,
        ),
    ):
        widget.track_seg.run_track_analysis()

        mock_show_info.assert_called_once_with(
            "Preventing analysis as user chose 'Cancel'"
        )


def test_run_track_analysis_show_info(
    segmentation_widget_with_data_atlas_space,
):
    widget = segmentation_widget_with_data_atlas_space

    with (
        patch(
            "brainglobe_segmentation.segmentation_panels.tracks.show_info"
        ) as mock_show_info,
        patch(
            "brainglobe_segmentation.segmentation_panels.tracks.display_warning",
            return_value=True,
        ),
        patch(
            "brainglobe_segmentation.segmentation_panels.tracks.track_analysis",
            return_value=(None, None),
        ),
    ):
        widget.track_seg.run_track_analysis()

        mock_show_info.assert_any_call("Running track analysis")
        mock_show_info.assert_any_call("Finished!")
