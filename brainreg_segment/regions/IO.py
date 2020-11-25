import imio
import numpy as np

from pathlib import Path
from skimage import measure

from imlib.general.pathlib import append_to_pathlib_stem


def convert_obj_to_br(verts, faces, voxel_size):
    if voxel_size != 1:
        verts = verts * voxel_size

    faces = faces + 1
    return verts, faces


def extract_and_save_object(
    image, output_file_name, voxel_size, threshold=0, step_size=1
):
    verts, faces, normals, values = measure.marching_cubes(
        image, threshold, step_size=step_size
    )
    verts, faces = convert_obj_to_br(verts, faces, voxel_size)
    marching_cubes_to_obj(
        (verts, faces, normals, values), str(output_file_name)
    )


def marching_cubes_to_obj(marching_cubes_out, output_file):
    """
    Saves the output of skimage.measure.marching_cubes as an .obj file
    :param marching_cubes_out: tuple
    :param output_file: str
    """

    verts, faces, normals, _ = marching_cubes_out
    with open(output_file, "w") as f:
        for item in verts:
            f.write(f"v {item[0]} {item[1]} {item[2]}\n")
        for item in normals:
            f.write(f"vn {item[0]} {item[1]} {item[2]}\n")
        for item in faces:
            f.write(
                f"f {item[0]}//{item[0]} {item[1]}//{item[1]} "
                f"{item[2]}//{item[2]}\n"
            )
        f.close()


def volume_to_vector_array_to_obj_file(
    image,
    output_path,
    voxel_size=50,
    step_size=1,
    threshold=0,
    deal_with_regions_separately=False,
):
    if deal_with_regions_separately:
        for label_id in np.unique(image):
            if label_id != 0:
                filename = append_to_pathlib_stem(
                    Path(output_path), "_" + str(label_id)
                )
                image = image == label_id
                extract_and_save_object(
                    image,
                    filename,
                    voxel_size,
                    threshold=threshold,
                    step_size=step_size,
                )
    else:
        extract_and_save_object(
            image,
            output_path,
            voxel_size,
            threshold=threshold,
            step_size=step_size,
        )


def save_label_layers(regions_directory, label_layers):
    print(f"Saving regions to: {regions_directory}")
    regions_directory.mkdir(parents=True, exist_ok=True)
    for label_layer in label_layers:
        save_regions_to_file(label_layer, regions_directory)


def export_label_layers(
    regions_directory, label_layers, voxel_size, obj_ext=".obj"
):
    print(f"Exporting regions to: {regions_directory}")
    regions_directory.mkdir(parents=True, exist_ok=True)
    for label_layer in label_layers:
        filename = regions_directory / (label_layer.name + obj_ext)
        export_regions_to_file(label_layer.data, filename, voxel_size)


def save_regions_to_file(
    label_layer,
    destination_directory,
    ignore_empty=True,
    image_extension=".tiff",
):
    """
    Saves the segmented regions to file (as .tiff)
    :param label_layer: napari labels layer (with segmented regions)
    :param destination_directory: Where to save files to
    :param ignore_empty: If True, don't attempt to save empty images
    :param image_extension: File extension fo the image files
    """
    data = label_layer.data
    if ignore_empty:
        if data.sum() == 0:
            return

    name = label_layer.name

    filename = destination_directory / (name + image_extension)
    imio.to_tiff(data.astype(np.int16), filename)


def export_regions_to_file(image, filename, voxel_size, ignore_empty=True):
    """
    Export regions as .obj for brainrender

    """
    if ignore_empty:
        if image.sum() == 0:
            return

    volume_to_vector_array_to_obj_file(image, filename, voxel_size=voxel_size)
