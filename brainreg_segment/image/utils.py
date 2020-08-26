import numpy as np
from scipy.spatial import cKDTree


def create_KDTree_from_image(image, value=0):
    """
    Create a KDTree of points equalling a given value
    :param image: Image to be converted to points
    :param value: Value of image to be used
    :return: scipy.spatial.cKDTree object
    """

    list_points = np.argwhere((image == value))
    return cKDTree(list_points)
