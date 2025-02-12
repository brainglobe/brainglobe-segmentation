import numpy as np

from brainglobe_segmentation.atlas import utils as atlas_utils


def test_lateralise_atlas_image(allen_mouse_50um_atlas):
    atlas = allen_mouse_50um_atlas

    mask = np.random.random(atlas.annotation.shape) > 0.7
    masked_annotations = mask * atlas.annotation
    annotations_left, annotations_right = atlas_utils.lateralise_atlas_image(
        masked_annotations,
        atlas.hemispheres,
        left_hemisphere_value=atlas.left_hemisphere_value,
        right_hemisphere_value=atlas.right_hemisphere_value,
    )

    # not the best way to test this is functioning properly
    total_vals_in = np.prod(mask.shape)
    total_vals_out = len(annotations_left) + len(annotations_right)

    assert total_vals_in == total_vals_out
