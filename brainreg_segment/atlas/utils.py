import re
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


def structure_from_viewer(status, atlas_layer, atlas):
    """
    Get brain region info from mouse position in napari viewer.

    Extract nx3 coordinate pair from napari window status string.
    Return brainglobe (BG) structure number, name, hemisphere, and a
    "pretty" string that can be displayed for example in the status bar.

    Parameter
    ---------
    status        : str, Napari viewer status (napari.viewer.Viewer.status)
    atlas_layer   : Napari viewer layer
                    Layer, which contains the annotation / region
                    information for every structure in the (registered)
                    atlas
    atlas         : Brainglobe atlas (bg_atlasapi.bg_atlas.BrainGlobeAtlas)

    Returns
    -------
    If any error is raised, (None,None,None,"") is returned
    structure_no  : int
                    BG Structure number
                    Returns none if not found
    structure     : str
                    Structure name
                    Returns none if not found
    hemisphere    : str
                    Hemisphere name
                    Returns none if not found
    region_info   : str
                    A string containing info about structure
                    and hemisphere
                    Returns empty string if not found
    """

    # Using a regex, extract list of coordinates from status string
    assert hasattr(atlas_layer, "data"), "Atlas layer appears to be empty"
    assert (
        atlas_layer.data.ndim == 3
    ), f'Atlas layer data does not have the right dim ("{atlas_layer.data.ndim}")'

    try:
        coords = re.findall(r"\[\d{1,5}\s+\d{1,5}\s+\d{1,5}\]", status)[0][
            1:-1
        ]
        coords_list = coords.split()
        map_object = map(int, coords_list)
        coord_list = tuple(map_object)
    except (IndexError, ValueError):
        # No coordinates could be extracted from status
        return None, None, None, ""

    # Extract structure number
    try:
        structure_no = atlas_layer.data[coord_list]
    except IndexError:
        return None, None, None, ""

    if structure_no in [0]:  # 0 is "Null" region
        return None, None, None, ""

    # Extract structure information
    try:
        structure = atlas.structures[structure_no]["name"]
    except KeyError:
        return None, None, None, ""

    # ... and make string pretty
    region_info = []
    for struct in structure.split(","):
        region_info.append(struct.strip().capitalize())
    hemisphere = atlas.hemisphere_from_coords(
        coord_list, as_string=True
    ).capitalize()
    region_info.append(hemisphere)
    region_info = " | ".join(region_info)

    return structure_no, structure, hemisphere, region_info
