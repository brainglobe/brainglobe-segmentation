import pandas as pd


def save_track_layers(
    tracks_directory, points_layers, track_file_extension=".points",
):
    print(f"Saving tracks to: {tracks_directory}")
    tracks_directory.mkdir(parents=True, exist_ok=True)

    for points_layer in points_layers:
        save_single_track(
            points_layer.data,
            points_layer.name,
            tracks_directory,
            track_file_extension=track_file_extension,
        )


def save_single_track(
    points, name, output_directory, track_file_extension=".points",
):
    output_filename = output_directory / (name + track_file_extension)
    points = pd.DataFrame(points)
    points.to_hdf(output_filename, key="df", mode="w")


def export_splines(
    tracks_directory, splines, spline_names, resolution, max_axis_2
):
    print(f"Exporting tracks to: {tracks_directory}")
    tracks_directory.mkdir(parents=True, exist_ok=True)

    for spline, name in zip(splines, spline_names):
        export_single_spline(
            spline, name, tracks_directory, resolution, max_axis_2
        )


def export_single_spline(
    spline,
    name,
    output_directory,
    resolution,
    max_axis_2,
    spline_file_extension=".h5",
):
    output_filename = output_directory / (name + spline_file_extension)
    points = pd.DataFrame(spline * resolution)
    points.columns = ["x", "y", "z"]
    # BR is oriented differently
    points["z"] = (max_axis_2 * resolution) - points["z"]
    points.to_hdf(output_filename, key="df", mode="w")
