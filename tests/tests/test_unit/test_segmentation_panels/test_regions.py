import numpy as np
from napari.layers import Labels

from brainreg_segment.segmentation_panels.regions import (
    check_segmentation_in_correct_space,
)


def test_check_segmentation_in_correct_space():
    labels_layer_10 = Labels(np.zeros((10, 10, 10), dtype=int))
    labels_layer_15 = Labels(np.zeros((15, 15, 15), dtype=int))
    assert check_segmentation_in_correct_space(
        [labels_layer_10], labels_layer_10.data
    )
    assert not check_segmentation_in_correct_space(
        [labels_layer_10], labels_layer_15.data
    )
