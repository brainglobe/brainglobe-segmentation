from unittest.mock import patch

import numpy as np
from napari.layers import Labels

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


def test_structure_from_viewer_no_hemispheres(allen_mouse_50um_atlas):
    atlas = allen_mouse_50um_atlas
    atlas_layer = Labels(atlas.annotation)

    with patch.object(type(atlas), "hemispheres", None):
        structure_no, structure, hemisphere, region_info = (
            atlas_utils.structure_from_viewer(
                (100, 100, 100), atlas_layer, atlas
            )
        )

    assert structure_no == 351
    assert structure == "Bed nuclei of the stria terminalis"
    assert hemisphere is None
    assert region_info == "Bed nuclei of the stria terminalis"
