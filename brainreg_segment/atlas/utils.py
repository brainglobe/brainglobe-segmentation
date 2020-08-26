from bg_atlasapi.list_atlases import utils, descriptors


def lateralise_atlas_image(
    masked_atlas_annotations,
    hemispheres,
    left_hemisphere_value=1,
    right_hemisphere_value=2,
):
    """
    :param masked_atlas_annotations: Masked image of atlas annotations
    :param hemispheres: Hemispheres image
    :param left_hemisphere_value: Value encoded in hemispheres image
    :param right_hemisphere_value: Value encoded in hemispheres image
    :return: Tuple (left, right) of numpy arrays of values within
    each hemisphere
    """
    annotation_left = masked_atlas_annotations[
        hemispheres == left_hemisphere_value
    ]
    annotation_right = masked_atlas_annotations[
        hemispheres == right_hemisphere_value
    ]
    return annotation_left, annotation_right


def get_available_atlases():
    """
    Get the available brainglobe atlases
    :return: Dict of available atlases (["name":version])
    """
    available_atlases = utils.conf_from_url(
        descriptors.remote_url_base.format("last_versions.conf")
    )
    available_atlases = dict(available_atlases["atlases"])
    return available_atlases


def display_brain_region_name(layer, structures):
    val = layer.get_value()
    if val != 0 and val is not None:
        try:
            msg = structures[val]["name"]
        except KeyError:
            msg = "Unknown region"
    else:
        msg = "No label here!"
    layer.help = msg
