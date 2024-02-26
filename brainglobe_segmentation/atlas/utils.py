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


def structure_from_viewer(coordinates, atlas_layer, atlas):
    """
    Get brain region info from mouse position in napari viewer.

    Return brainglobe (BG) structure number, name, hemisphere, and a
    "pretty" string that can be displayed for example in the status bar.

    Parameter
    ---------
    coordinates   : tuple, nx3 coordinate of cursor position, from
                    Viewer.cursor.position
    atlas_layer   : Napari viewer layer
                    Layer, which contains the annotation / region
                    information for every structure in the (registered)
                    atlas
    atlas         : Brainglobe atlas
                    (brainglobe_atlasapi.bg_atlas.BrainGlobeAtlas)

    Returns
    -------

    region_info   : str
                    A string containing info about structure
                    and hemisphere
                    Returns empty string if not found
    """

    # Using a regex, extract list of coordinates from status string
    assert hasattr(atlas_layer, "data"), "Atlas layer appears to be empty"
    assert atlas_layer.data.ndim == 3, (
        "Atlas layer data does not have the right dim "
        f'("{atlas_layer.data.ndim}")'
    )

    coord_list = tuple([int(x) for x in coordinates])

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
