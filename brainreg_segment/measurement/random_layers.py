import numpy as np


def generate_random_points_3d_layer(shape=(10, 3)):
    data = np.random.rand(*shape) * 100.0
    return [(data, {"name": "random 3d"}, "points")]


def generate_random_points_2d_layer(shape=(10, 2)):
    data = np.random.rand(*shape) * 100.0
    return [(data, {"name": "random 2d"}, "points")]
