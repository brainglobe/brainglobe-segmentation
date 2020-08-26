import pandas as pd

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
        spline = spline_fit(
            track_layer.data,
            smoothing=spline_smoothing,
            k=fit_degree,
            n_points=spline_points,
        )
        splines.append(spline)
        if summarise_track:
            summary_csv_file = tracks_directory / (track_layer.name + ".csv")
            analyse_track_anatomy(atlas, spline, summary_csv_file)

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


def analyse_track_anatomy(atlas, spline, file_path, verbose=True):
    """
    For a given spline, and brainrender scene, find the brain region that each
    "segment" is in, and save to csv.

    :param scene: brainrender scene object
    :param spline: numpy array defining the spline interpolation
    :param file_path: path to save the results to
    :param bool verbose: Whether to print the progress
    """
    if verbose:
        print("Determining the brain region for each segment of the spline")
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
    if verbose:
        print(f"Saving results to: {file_path}")
    df.to_csv(file_path, index=False)
