from pathlib import Path

import pandas as pd
from napari.layers import Points


def add_new_track_layer(viewer, track_layers, point_size):
    num = len(track_layers)
    new_track_layers = viewer.add_points(
        ndim=3,
        n_dimensional=True,
        size=point_size,
        name=f"track_{num}",
    )
    new_track_layers.mode = "ADD"
    track_layers.append(new_track_layers)


def add_existing_track_layers(viewer, track_file, point_size):
    points = pd.read_hdf(track_file)
    new_points_layer = viewer.add_points(
        points,
        n_dimensional=True,
        size=point_size,
        name=Path(track_file).stem,
    )
    new_points_layer.mode = "ADD"
    return new_points_layer


def add_track_from_existing_layer(selected_layer, track_layers):
    """
    Adds an existing tracks layer (e.g. from another plugin) to the list
    """
    if isinstance(selected_layer, Points):
        track_layers.append(selected_layer)
    else:
        raise TypeError("Layer must be a napari Points layer")
