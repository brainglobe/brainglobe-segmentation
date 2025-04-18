import numpy as np
import pandas as pd
from scipy.spatial.distance import euclidean

from brainglobe_segmentation.tracks.fit import spline_fit


def track_analysis(
    viewer,
    annotations_layer_image,
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
                annotations_layer_image,
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
                border_color="cyan",
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
    annotations_layer_image,
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
    :param annotations_layer_image: 3D numpy array of the (possibly registered)
    annotations image
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
    # 2 stage process to ensure ordering
    _, indices = np.unique(points, return_index=True, axis=0)
    points = points[np.sort(indices)]

    spline = spline_fit(
        points,
        smoothing=spline_smoothing,
        k=fit_degree,
        n_points=spline_points,
    )
    if summarise_track:
        summary_csv_file = tracks_directory / (track_name + ".csv")
        analyse_track_anatomy(
            annotations_layer_image, atlas, spline, summary_csv_file
        )

    return spline


def get_distances(spline, voxel_size=10):
    """
    For a given spline, calculate the distance between each point.
    Assumes a customisable isotropic voxel size (default 10) in microns.
    """
    distances = [0]
    for i in range(len(spline) - 1):
        distance = round(euclidean(spline[i], spline[i + 1]) * voxel_size, 3)
        distances.append(distances[i] + distance)
    return distances


def analyse_track_anatomy(annotations_layer_image, atlas, spline, file_path):
    """
    For a given spline, find the atlas region that each
    "segment" is in, and save to csv.

    :param annotations_layer_image: 3D numpy array of the (possibly registered)
    annotations image
    :param atlas: brainglobe atlas class
    :param spline: numpy array defining the spline interpolation
    :param file_path: path to save the results to
    :param bool verbose: Whether to print the progress
    """
    spline_regions = []
    for coord in spline.tolist():
        try:
            coord = tuple(int(c) for c in coord)
            atlas_value = annotations_layer_image[coord]
            spline_regions.append(atlas.structures[atlas_value])
        except KeyError:
            spline_regions.append(None)

    distances = get_distances(spline, voxel_size=atlas.resolution[0])

    df = pd.DataFrame(
        columns=[
            "Index",
            "Distance from first position [um]",
            "Region ID",
            "Region acronym",
            "Region name",
        ]
    )
    for idx, spline_region in enumerate(spline_regions):
        if spline_region is None:
            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        [
                            {
                                "Index": idx,
                                "Distance from first position [um]": distances[
                                    idx
                                ],
                                "Region ID": "Not found in brain",
                                "Region acronym": "Not found in brain",
                                "Region name": "Not found in brain",
                            }
                        ]
                    ),
                ]
            )

        else:
            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        [
                            {
                                "Index": idx,
                                "Distance from first position [um]": distances[
                                    idx
                                ],
                                "Region ID": spline_region["id"],
                                "Region acronym": spline_region["acronym"],
                                "Region name": spline_region["name"],
                            }
                        ]
                    ),
                ]
            )

    df.to_csv(file_path, index=False)
