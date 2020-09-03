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


def make_structure_info_string(status_string, atlas, coord_list=None):
    """
    Get brain region info.

    Extract nx3 coordinate pair from napari window status string.
    Return structure number (atlas.structure_from_coords)
    and name.

    Parameter
    ---------
    status_string : str
                    napari viewer.status
    atlas         : reference atlas (bg atlas)
    coord_list    : (optional) list
                    List of coordinates (nx3)

    Returns
    -------
    If any error is raised, ('',None,None,None) is returned
    region_info   : str
                    A nice string containing info about structure
                    and hemisphere
    structure_no  : int
                    Structure number
    structure     : str
                    Structure name
    hemisphere    : str
                    Hemisphere name

    """

    if coord_list is not None:
        assert isinstance(coord_list, list) and (len(coord_list) == 3)
    else:
        # Using a regex, extract list of coordinates from status string
        try:
            coords = re.findall(
                r"\[\d{1,5}\s+\d{1,5}\s+\d{1,5}\]", status_string
            )[0][1:-1]
            coords_list = coords.split()
            map_object = map(int, coords_list)
            coord_list = list(map_object)
        except (IndexError, ValueError):
            # No coordinates could be retrieved
            return "", None, None, None

    # Extract structure number
    structure_no = ""

    try:
        structure_no = atlas.structure_from_coords(coord_list)
    except IndexError:
        return "", None, None, None
    if structure_no in [0]:  # 0 is "Null" region
        return "", None, None, None

    # Extract structure information
    structure = atlas.structures[structure_no]["name"]
    # ... and make string pretty
    region_info = []
    for struct in structure.split(","):
        region_info.append(struct.strip().capitalize())
    hemisphere = atlas.hemisphere_from_coords(
        coord_list, as_string=True
    ).capitalize()
    region_info.append(hemisphere)
    region_info = " | ".join(region_info)

    return region_info, structure_no, structure, hemisphere
