from unittest.mock import patch


def test_add_new_region_button_log(segmentation_widget_with_data_atlas_space):
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
