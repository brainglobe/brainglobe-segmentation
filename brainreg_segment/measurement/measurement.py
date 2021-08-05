import os
import csv
from enum import Enum
import math
import pathlib
from typing import List, Tuple, Optional, TYPE_CHECKING

import numpy as np
from napari_plugin_engine import napari_hook_implementation


if TYPE_CHECKING:
    import napari



# For the axis I will assume the following (x,y,z) are each of the following
#  (anteroposterior, mediolateral, vectical)
def get_angles_and_distances_between_consecutive_points(
    point_layer: "napari.layers.Points") -> Tuple[List[float]]:
    """
    TODO: pending docstring and output types
    TODO: Assumed points are always 3d, be careful when that's not the case
    https://forum.image.sc/t/controlling-dimensionality-of-napari-point-shape-layers/37896/2
    """
    points_array  = point_layer.data
    n_points = points_array.shape[0]
    ap_angles = []
    mp_angles = []
    distances = []
    for i in range(1, n_points):
        pointA = points_array[i-1, :]
        pointB = points_array[i, :]
        segment_vector = pointB - pointA
        # projecting the vector in the sagital plane is just removing
        #  the "y/mediolateral" coordinate
        segment_vector_zx = segment_vector[[2,0]]
        # for the angle, z is used as the first direction/axis and x as the other 
        ap_angle = math.atan2(segment_vector_zx[1], segment_vector_zx[0])
        ap_angles.append(ap_angle)
        # projecting the vector in the frontal plane is just removing
        #  the anterioposterior coordinate.
        segment_vector_zy = segment_vector[[2,1]]
        # for the angle, z is used as the first direction/axis and y as the other 
        mp_angle = math.atan2(segment_vector_zy[1], segment_vector_zy[0])
        mp_angles.append(mp_angle)
        distances.append(np.linalg.norm(segment_vector))
    return ap_angles, mp_angles, distances


def analyze_points_layer(point_layer: "napari.layers.Points",
                         output_folder: str='point_analysis'):
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
        point_layer: A points layer to analyze
        output_folder: Name of the folder where the output is going to be saved


    """
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    
    assert len(point_layer.data) > 0, 'Not enough points in the layer'


    (ap_angles, mp_angles,
     distances) = get_angles_and_distances_between_consecutive_points(point_layer)

    with open(os.path.join(output_folder,'measurements.csv'), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(('point1_id', 'point2_id', 'AP_angle', 'MP_angle', 'distance'))
        for i in range(len(mp_angles)):
            writer.writerow((i, i+1, ap_angles[i], mp_angles[i], distances[i]))
    
    points_array  = point_layer.data
    n_points = points_array.shape[0]
    n_coords = points_array.shape[1]


    with open(os.path.join(output_folder,'points.csv'), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(('point_id', *(f'coord_{i}' for i in range(n_coords))))
        for i in range(n_points):
            writer.writerow((i, *points_array[i]))

    print(f'created analysis folder at folder called: {output_folder}')