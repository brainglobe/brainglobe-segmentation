from bg_atlasapi.list_atlases import utils, descriptors


def lateralise_atlas_image(
    atlas, hemispheres, left_hemisphere_value=1, right_hemisphere_value=2
):
    atlas_left = atlas[hemispheres == left_hemisphere_value]
    atlas_right = atlas[hemispheres == right_hemisphere_value]
    return atlas_left, atlas_right


def get_available_atlases():
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
