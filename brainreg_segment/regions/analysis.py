import numpy as np
import pandas as pd


from napari.qt.threading import thread_worker
from skimage.measure import regionprops_table

from imlib.pandas.misc import initialise_df
from imlib.general.list import unique_elements_lists

from brainreg_segment.atlas.utils import lateralise_atlas_image


@thread_worker
def region_analysis(
    label_layers,
    atlas_layer_image,
    atlas,
    hemispheres,
    regions_directory,
    output_csv_file=None,
    volumes=True,
    summarise=True,
):
    regions_directory.mkdir(parents=True, exist_ok=True)
    if volumes:
        print("Calculating region volume distribution")
        print(f"Saving summary volumes to: {regions_directory}")
        for label_layer in label_layers:
            analyse_region_brain_areas(
                label_layer,
                atlas_layer_image,
                hemispheres,
                regions_directory,
                atlas,
            )
    if summarise:
        if output_csv_file is not None:
            print("Summarising regions")
            summarise_brain_regions(
                label_layers, output_csv_file, atlas.resolution
            )

    print("Finished!\n")


def summarise_brain_regions(label_layers, filename, atlas_resolution):
    summaries = []
    for label_layer in label_layers:
        summaries.append(summarise_single_brain_region(label_layer))

    result = pd.concat(summaries)
    # TODO: use atlas.space to make these more intuitive
    volume_header = "volume_mm3"
    length_columns = [
        "axis_0_min_um",
        "axis_1_min_um",
        "axis_2_min_um",
        "axis_0_max_um",
        "axis_1_max_um",
        "axis_2_max_um",
        "axis_0_center_um",
        "axis_1_center_um",
        "axis_2_center_um",
    ]

    result.columns = ["region"] + [volume_header] + length_columns

    voxel_volume_in_mm = np.prod(atlas_resolution) / (1000 ** 3)

    result[volume_header] = result[volume_header] * voxel_volume_in_mm

    for header in length_columns:
        for dim, idx in enumerate(atlas_resolution):
            if header.startswith(f"axis_{dim}"):
                scale = float(idx)
                assert scale > 0
                result[header] = result[header] * scale

    result.to_csv(filename, index=False)


def summarise_single_brain_region(
    label_layer,
    ignore_empty=True,
    properties_to_fetch=[
        "area",
        "bbox",
        "centroid",
    ],
):
    data = label_layer.data
    if ignore_empty:
        if data.sum() == 0:
            return

    regions_table = regionprops_table(
        data.astype(np.uint16), properties=properties_to_fetch
    )
    df = pd.DataFrame.from_dict(regions_table)
    df.insert(0, "Region", label_layer.name)
    return df


def analyse_region_brain_areas(
    label_layer,
    atlas_layer_data,
    hemispheres,
    destination_directory,
    atlas,
    extension=".csv",
    ignore_empty=True,
):
    """

    :param label_layer: napari labels layer (with segmented regions)

    :param ignore_empty: If True, don't analyse empty regions
    """

    data = label_layer.data
    if ignore_empty:
        if data.sum() == 0:
            return

    name = label_layer.name

    masked_annotations = data.astype(bool) * atlas_layer_data

    annotations_left, annotations_right = lateralise_atlas_image(
        masked_annotations,
        hemispheres,
        left_hemisphere_value=atlas.left_hemisphere_value,
        right_hemisphere_value=atlas.right_hemisphere_value,
    )

    unique_vals_left, counts_left = np.unique(
        annotations_left, return_counts=True
    )
    unique_vals_right, counts_right = np.unique(
        annotations_right, return_counts=True
    )
    voxel_volume_in_mm = np.prod(atlas.resolution) / (1000 ** 3)

    df = initialise_df(
        "structure_name",
        "left_volume_mm3",
        "left_percentage_of_total",
        "right_volume_mm3",
        "right_percentage_of_total",
        "total_volume_mm3",
        "percentage_of_total",
    )

    sampled_structures = unique_elements_lists(
        list(unique_vals_left) + list(unique_vals_right)
    )
    total_volume_region = get_total_volume_regions(
        unique_vals_left, unique_vals_right, counts_left, counts_right
    )

    for atlas_value in sampled_structures:
        if atlas_value != 0:
            try:
                df = add_structure_volume_to_df(
                    df,
                    atlas_value,
                    atlas.structures,
                    unique_vals_left,
                    unique_vals_right,
                    counts_left,
                    counts_right,
                    voxel_volume_in_mm,
                    total_volume_voxels=total_volume_region,
                )

            except KeyError:
                print(
                    f"Value: {atlas_value} is not in the atlas structure"
                    f" reference file. Not calculating the volume"
                )
    filename = destination_directory / (name + extension)
    df.to_csv(filename, index=False)


def get_total_volume_regions(
    unique_vals_left,
    unique_vals_right,
    counts_left,
    counts_right,
):
    zero_index_left = np.where(unique_vals_left == 0)[0][0]
    counts_left = list(counts_left)
    counts_left.pop(zero_index_left)

    zero_index_right = np.where(unique_vals_right == 0)[0][0]
    counts_right = list(counts_right)
    counts_right.pop(zero_index_right)

    return sum(counts_left + counts_right)


def add_structure_volume_to_df(
    df,
    atlas_value,
    atlas_structures,
    unique_vals_left,
    unique_vals_right,
    counts_left,
    counts_right,
    voxel_volume,
    total_volume_voxels=None,
):
    name = atlas_structures[atlas_value]["name"]

    left_volume, left_percentage = get_volume_in_hemisphere(
        atlas_value,
        unique_vals_left,
        counts_left,
        total_volume_voxels,
        voxel_volume,
    )
    right_volume, right_percentage = get_volume_in_hemisphere(
        atlas_value,
        unique_vals_right,
        counts_right,
        total_volume_voxels,
        voxel_volume,
    )
    if total_volume_voxels is not None:
        total_percentage = left_percentage + right_percentage
    else:
        total_percentage = 0

    df = df.append(
        {
            "structure_name": name,
            "left_volume_mm3": left_volume,
            "left_percentage_of_total": left_percentage,
            "right_volume_mm3": right_volume,
            "right_percentage_of_total": right_percentage,
            "total_volume_mm3": left_volume + right_volume,
            "percentage_of_total": total_percentage,
        },
        ignore_index=True,
    )
    return df


def get_volume_in_hemisphere(
    atlas_value, unique_vals, counts, total_volume_voxels, voxel_volume
):
    try:
        index = np.where(unique_vals == atlas_value)[0][0]
        volume = counts[index] * voxel_volume
        if total_volume_voxels is not None:
            percentage = 100 * (counts[index] / total_volume_voxels)
        else:
            percentage = 0
    except IndexError:
        volume = 0
        percentage = 0

    return volume, percentage
