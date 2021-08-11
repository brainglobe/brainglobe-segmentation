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
else:
  # added by jm
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
    # projecting the vector in the sagital plane is just removing
    #  the "y/mediolateral" coordinate
    segment_vector_zx = segment_vector[[2, 0]]
    # for the angle, z is used as the first direction/axis and x as the other
    ap_angle = math.atan2(segment_vector_zx[1], segment_vector_zx[0])
    ap_angles.append(ap_angle)
    # projecting the vector in the frontal plane is just removing
    #  the anterioposterior coordinate.
    segment_vector_zy = segment_vector[[2, 1]]
    # for the angle, z is used as the first direction/axis and y as the other
    mp_angle = math.atan2(segment_vector_zy[1], segment_vector_zy[0])
    mp_angles.append(mp_angle)
    distances.append(np.linalg.norm(segment_vector))
  return ap_angles, mp_angles, distances


def get_vectors_joining_points(point_layer: "napari.layers.Points") -> np.array:

  points_array = point_layer.data
  n_points = points_array.shape[0]
  n_coords = points_array.shape[1]
  if n_points < 2:
    return

  pointsb = points_array[1:]
  pointsa = points_array[:-1]

  arrays = np.stack([pointsa, pointsb], axis=1)
  return arrays


def analyze_points_layer(
    point_layer: "napari.layers.Points",
    output_folder: str = 'point_analysis') -> "napari.layers.Shapes":
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

  with open(os.path.join(output_folder, 'measurements.csv'), 'w',
            newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(
        ('point1_id', 'point2_id', 'AP_angle', 'MP_angle', 'distance'))
    for i in range(len(mp_angles)):
      writer.writerow((i, i + 1, ap_angles[i], mp_angles[i], distances[i]))

  points_array = point_layer.data
  n_points = points_array.shape[0]
  n_coords = points_array.shape[1]

  with open(os.path.join(output_folder, 'points.csv'), 'w',
            newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(('point_id', *(f'coord_{i}' for i in range(n_coords))))
    for i in range(n_points):
      writer.writerow((i, *points_array[i]))

  print(f'created analysis files at folder called: {output_folder}')

  lines_joining_consecutive_points = get_vectors_joining_points(point_layer)
  properties_dict = {
      'distance': distances,
      'ap_angle': ap_angles,
      'mp_angle': mp_angles
  }

  text_parameters = {
      'text':
          'distance: {distance:.4f}\nap_angle: {ap_angle:.4f}\n mp_angle: {mp_angle:.4f}',
      'size':
          8,
      'color':
          'green',
      'anchor':
          'upper_left',
      'translation': [-2, 0., 0.]
                     if point_layer.data.shape[1] == 3 else [-2, 0.]
  }
  # addng vectors as a layer
  lines_layer = napari.layers.Shapes(data=lines_joining_consecutive_points,
                                     shape_type='path',
                                     edge_color='blue',
                                     properties=properties_dict,
                                     text=text_parameters,
                                     edge_width=0.1)
  return lines_layer
