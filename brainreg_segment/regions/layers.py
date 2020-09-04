import tifffile
import numpy as np

from glob import glob
from pathlib import Path


def add_new_label_layer(
    viewer,
    base_image,
    name="region",
    selected_label=1,
    num_colors=10,
    brush_size=30,
):
    """
    Takes an existing napari viewer, and adds a blank label layer
    (same shape as base_image)
    :param viewer: Napari viewer instance
    :param np.array base_image: Underlying image (for the labels to be
    referencing)
    :param str name: Name of the new labels layer
    :param int selected_label: Label ID to be preselected
    :param int num_colors: How many colors (labels)
    :param int brush_size: Default size of the label brush
    :return label_layer: napari labels layer
    """
    labels = np.empty_like(base_image)
    label_layer = viewer.add_labels(labels, num_colors=num_colors, name=name)
    label_layer.n_dimensional = True
    label_layer.selected_label = selected_label
    label_layer.brush_size = brush_size
    return label_layer


def add_new_region_layer(
    viewer, label_layers, image_like, brush_size, num_colors
):
    num = len(label_layers)
    new_label_layer = add_new_label_layer(
        viewer,
        image_like,
        name=f"region_{num}",
        brush_size=brush_size,
        num_colors=num_colors,
    )
    new_label_layer.mode = "PAINT"
    label_layers.append(new_label_layer)


def add_existing_label_layers(
    viewer,
    label_file,
    selected_label=1,
    num_colors=10,
    brush_size=30,
):
    """
    Loads an existing image as a napari labels layer
    :param viewer: Napari viewer instance
    :param label_file: Filename of the image to be loaded
    :param int selected_label: Label ID to be preselected
    :param int num_colors: How many colors (labels)
    :param int brush_size: Default size of the label brush
    :return label_layer: napari labels layer
    """
    label_file = Path(label_file)
    labels = tifffile.imread(label_file)
    label_layer = viewer.add_labels(
        labels, num_colors=num_colors, name=label_file.stem
    )
    label_layer.selected_label = selected_label
    label_layer.brush_size = brush_size
    return label_layer


def add_existing_region_segmentation(
    directory, viewer, label_layers, file_extension
):
    label_files = glob(str(directory) + "/*" + file_extension)
    if directory and label_files != []:
        for label_file in label_files:
            label_layers.append(add_existing_label_layers(viewer, label_file))
