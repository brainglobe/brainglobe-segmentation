import numpy as np
from bg_atlasapi import BrainGlobeAtlas

from brainreg_segment.atlas import utils as atlas_utils

atlas_name = "allen_mouse_50um"


def test_get_available_atlases():
    atlases = atlas_utils.get_available_atlases()

    # arbitrary selection of atlases
    assert float(atlases["allen_mouse_10um"]) >= 0.3
    assert float(atlases["allen_mouse_25um"]) >= 0.3
    assert float(atlases["allen_mouse_50um"]) >= 0.3
    assert float(atlases["mpin_zfish_1um"]) >= 0.4


def test_lateralise_atlas_image():
    atlas = BrainGlobeAtlas(atlas_name)

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
