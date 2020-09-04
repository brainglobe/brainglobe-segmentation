import numpy as np
from scipy.interpolate import splprep, splev


def spline_fit(points, smoothing=0.2, k=3, n_points=100):
    """Given an input set of 2/3D points, returns a new set of points
    representing the spline interpolation
    Parameters
    ----------
    points : np.ndarray
        2/3D array of points defining a path
    smoothing : float
        Smoothing factor
    k : int
        Spline degree
    n_points : int
        How many points used to define the resulting interpolated path
    Returns
    ----------
    new_points : np.ndarray
        Points defining the interpolation
    """

    # scale smoothing to the spread of the points
    max_range = max(np.max(points, axis=0) - np.min(points, axis=0))
    smoothing *= max_range

    # calculate bspline representation
    tck, _ = splprep(points.T, s=smoothing, k=k)

    # evaluate bspline
    spline_fit_points = splev(np.linspace(0, 1, n_points), tck)

    return np.array(spline_fit_points).T
