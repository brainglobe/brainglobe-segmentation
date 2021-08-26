import csv
import math
import os
import pathlib
from typing import List, Tuple

from magicgui import magic_factory
import napari
import numpy as np


# For the axis This assumes the following (x,y,z) are each of the following
#  (anteroposterior, mediolateral, vectical)
def get_angles_and_distances_between_consecutive_points(
    point_layer: "napari.layers.Points",
) -> Tuple[List[float]]:
    """Returns the distance and angles  for each pair of consecutive points.

    Receives a points layer and for each pair of consecutive points it
    generates a vector, the anterioposterior and mediolateral angles of those
    vectors are returned together with the magnitude of the vectors.

    Args:
        point_layer: A napari point layer with at least two points.
    Returns:
        Three lists, one contains the anterioposterior angles, the other
        contains the mediolateral angles and the last one contains the distance
        between each points. All the lists are of length = point_layer - 1
    """
    points_array = point_layer.data

    n_points = points_array.shape[0]
    n_coords = points_array.shape[1]

    if n_coords == 2:
        points_array = np.hstack([points_array, np.zeros((n_points, 1))])

    ap_angles = []
    mp_angles = []
    distances = []
    for i in range(1, n_points):
        pointa = points_array[i - 1, :]
        pointb = points_array[i, :]
        segment_vector = pointa - pointb
        # projecting the vector in the sagital plane is just removing
        #  the "y/mediolateral" coordinate
        segment_vector_zx = segment_vector[[2, 0]]
        # for the angle, z is used as the first direction/axis and x as the other
        ap_angle = math.atan2(segment_vector_zx[1], segment_vector_zx[0])
        ap_angles.append(ap_angle)
        # projecting the vector in the frontal plane is just removing
        #  the anterioposterior coordinate.
        segment_vector_zy = segment_vector[[2, 1]]
        # for the angle, z is used as the first direction/axis and y as the other
        mp_angle = math.atan2(segment_vector_zy[1], segment_vector_zy[0])
        mp_angles.append(mp_angle)
        distances.append(np.linalg.norm(segment_vector))
    return ap_angles, mp_angles, distances


def get_vectors_joining_points(
    point_layer: "napari.layers.Points",
) -> np.array:
    """Returns an array of the vectors joining each pair of consecutive points.

    Receives a napari points layer whose data attribute must be
    (n_points, n_dims) and returns an array of the vectors joining each pair of
    consecutive points.

    Args:
        point_layer: Napari points layer with at least two points. Shape
            of point_layer.data must be (n_points, n_dims).
    Returns:
        A numpy array of shape (n_points - 1, 2, n_dims) where the first
        dimension corresponds to the 'n_points' - 1 lines that join all
        the pairs of consecutive points in point_layer.data. The second
        dimension, is a 2 because it contains the initial and end point
        of the line.
    """
    points_array = point_layer.data
    n_points = points_array.shape[0]
    if n_points < 2:
        raise ValueError(
            "Expected at least two points in order to run the plugin"
        )

    pointsb = points_array[1:]
    pointsa = points_array[:-1]

    arrays = np.stack([pointsa, pointsb], axis=1)
    return arrays


@magic_factory(
    auto_call=False,
    output_folder={"mode": "d"},
    call_button=True,
    save_resuts_to_output_folder={"label": "Save results to output folder?"},
)
def analyze_points_layer(
    point_layer: "napari.layers.Points",
    save_resuts_to_output_folder: bool = False,
    output_folder: pathlib.Path = "results_folder",
) -> List[napari.types.LayerDataTuple]:
    """Analyzes a point layer and saves distances and angles for consecutive points
    points.csv
    id, coordx,  coordy,  coordz
    0,   ..
    1,   ..
    measurements.csv

    the angles define the vector from point 1 to point2

    point1_id, point2_id, distances, AP_angle, MP_angle
    0,         ..
    1,         ..

    Args:
        point_layer: A points layer to analyze.
        save_resuts_to_output_folder: A boolean, whether to save the results
            to the output folder below. If False, output_folder is ignored.
        output_folder: Name of the folder where the output is going to be saved.
    """
    if save_resuts_to_output_folder and not os.path.exists(output_folder):
        os.mkdir(output_folder)

    assert len(point_layer.data) > 0, "Not enough points in the layer"

    (
        ap_angles,
        mp_angles,
        distances,
    ) = get_angles_and_distances_between_consecutive_points(point_layer)

    points_array = point_layer.data
    n_points = points_array.shape[0]
    n_coords = points_array.shape[1]

    if save_resuts_to_output_folder:
        with open(
            os.path.join(output_folder, "measurements.csv"), "w", newline=""
        ) as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(
                ("point1_id", "point2_id", "AP_angle", "MP_angle", "distance")
            )
            for i in range(len(mp_angles)):
                writer.writerow(
                    (i, i + 1, ap_angles[i], mp_angles[i], distances[i])
                )

        with open(
            os.path.join(output_folder, "points.csv"), "w", newline=""
        ) as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(
                ("point_id", *(f"coord_{i}" for i in range(n_coords)))
            )
            for i in range(n_points):
                writer.writerow((i, *points_array[i]))

        print(f"created analysis files at folder called: {output_folder}")

    lines_joining_consecutive_points = get_vectors_joining_points(point_layer)

    vectors_props = {
        "distance": distances,
        "ap_angle": ap_angles,
        "mp_angle": mp_angles,
    }

    # Adding vectors as a shapes layer.
    vectors_text = {
        "text": "distance: {distance:.4f}\nap_angle: {ap_angle:.4f}\n mp_angle: {mp_angle:.4f}",
        "size": 8,
        "color": "green",
        "anchor": "upper_left",
        "translation": [-2, 0.0, 0.0]
        if point_layer.data.shape[1] == 3
        else [-2, 0.0],
    }

    lines_layer_meta = {
        "shape_type": "path",
        "edge_color": "blue",
        "properties": vectors_props,
        "text": vectors_text,
        "edge_width": 0.1,
    }

    # Adding a new point layers with the text to show the index of each point.
    points_annotations_properties = {"index": list(range(1, n_points + 1))}

    points_annotations_text = {
        "text": "Point {index}",
        "size": 8,
        "color": "red",
        "anchor": "upper_left",
        "translation": [0.0, 0.0, 0.0]
        if point_layer.data.shape[1] == 3
        else [0.0, 0.0],
    }

    numbered_points_meta = {
        "properties": points_annotations_properties,
        "text": points_annotations_text,
        "edge_color": "transparent",
        "face_color": "transparent",
    }

    return [
        (lines_joining_consecutive_points, lines_layer_meta, "shapes"),
        (point_layer.data, numbered_points_meta, "points"),
    ]
