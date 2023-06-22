from brainreg_segment.segmentation_panels.regions import (
    check_segmentation_in_correct_space,
)


# Perhaps overkill to use these two fixtures, but it's close to
# the errors that could occur during use
def test_check_segmentation_in_correct_space(
    segmentation_widget_with_data_sample_space,
    segmentation_widget_with_data_atlas_space,
):
    annotations_layer_data = (
        segmentation_widget_with_data_sample_space.annotations_layer.data
    )
    mock_labels_layers = [
        segmentation_widget_with_data_atlas_space.annotations_layer.data
    ]
    assert (
        check_segmentation_in_correct_space(
            mock_labels_layers, annotations_layer_data
        )
        is False
    )
