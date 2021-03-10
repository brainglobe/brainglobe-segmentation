import pandas as pd
import numpy as np
from brainreg_segment.tracks.fit import spline_fit


def track_analysis(
    viewer,
    atlas,
    tracks_directory,
    track_layers,
    napari_spline_size,
    spline_points=100,
    fit_degree=3,
    spline_smoothing=0.05,
    summarise_track=True,
):
    tracks_directory.mkdir(parents=True, exist_ok=True)

    print(
        f"Fitting splines with {spline_points} segments, of degree "
        f"'{fit_degree}' to the points"
    )
    splines = []
    spline_names = []

    for track_layer in track_layers:
        if len(track_layer.data) != 0:
            spline = run_track_analysis(
                track_layer.data,
                track_layer.name,
                tracks_directory,
                atlas,
                summarise_track=summarise_track,
                spline_smoothing=spline_smoothing,
                spline_points=spline_points,
                fit_degree=fit_degree,
            )

            splines.append(spline)

            viewer.add_points(
                spline,
                size=napari_spline_size,
                edge_color="cyan",
                face_color="cyan",
                blending="additive",
                opacity=0.7,
                name=track_layer.name + "_fit",
            )

            spline_names.append(track_layer.name)
    return splines, spline_names


def run_track_analysis(
    points,
    track_name,
    tracks_directory,
    atlas,
    spline_smoothing=0.05,
    spline_points=100,
    fit_degree=3,
    summarise_track=True,
):
    """
    For each set of points, run a spline fit, and (if required) determine which
     atlas region each part of the spline fit is within
    :param points: 3D numpy array of points
    :param track_name: Name of the set of points (used for saving results)
    :param tracks_directory: Where to save the results to
    :param atlas: brainglobe atlas class
    :param spline_smoothing: spline fit smoothing factor
    :param spline_points: How many points used to define the resulting
    interpolated path
    :param fit_degree: spline fit degree
    :param summarise_track: If True, save a csv with the atlas region for
    all parts of the spline fit
    :return np.array: spline fit
    """
    # Duplicate points causes fit ValueError
    points = np.unique(points, axis=0)

    spline = spline_fit(
        points,
        smoothing=spline_smoothing,
        k=fit_degree,
        n_points=spline_points,
    )
    if summarise_track:
        summary_csv_file = tracks_directory / (track_name + ".csv")
        analyse_track_anatomy(atlas, spline, summary_csv_file)

    return spline


def analyse_track_anatomy(atlas, spline, file_path):
    """
    For a given spline, find the atlas region that each
    "segment" is in, and save to csv.

    :param atlas: brainglobe atlas class
    :param spline: numpy array defining the spline interpolation
    :param file_path: path to save the results to
    :param bool verbose: Whether to print the progress
    """
    spline_regions = []
    for p in spline.tolist():
        try:
            spline_regions.append(
                atlas.structures[atlas.structure_from_coords(p)]
            )
        except KeyError:
            spline_regions.append(None)

    df = pd.DataFrame(
        columns=["Position", "Region ID", "Region acronym", "Region name"]
    )
    for idx, spline_region in enumerate(spline_regions):
        if spline_region is None:
            df = df.append(
                {
                    "Position": idx,
                    "Region ID": "Not found in brain",
                    "Region acronym": "Not found in brain",
                    "Region name": "Not found in brain",
                },
                ignore_index=True,
            )
        else:
            df = df.append(
                {
                    "Position": idx,
                    "Region ID": spline_region["id"],
                    "Region acronym": spline_region["acronym"],
                    "Region name": spline_region["name"],
                },
                ignore_index=True,
            )
    df.to_csv(file_path, index=False)
