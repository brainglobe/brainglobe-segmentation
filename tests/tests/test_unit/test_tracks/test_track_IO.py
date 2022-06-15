from pathlib import Path

import numpy as np
import pandas as pd

from brainreg_segment.tracks import IO

tracks_dir = Path.cwd() / "tests" / "data" / "tracks"

pts_2d = np.array([[53, 748], [68, 745], [77, 747], [87, 748], [97, 749]])


spline = np.array(
    (
        [100.0, 49.81249744, 50.08749819],
        [100.0, 58.06928727, 58.53487443],
        [100.0, 66.38765117, 66.9206766],
        [100.0, 74.74999655, 75.26249729],
        [100.0, 83.13873081, 83.57792909],
        [100.0, 91.53626138, 91.8845646],
        [100.0, 99.92499565, 100.1999964],
        [100.0, 108.28734103, 108.54181709],
        [100.0, 116.60570493, 116.92761926],
        [100.0, 124.86249475, 125.3749955],
    )
)

ATLAS_RESOLUTION = 50


def test_save_single_track_layer(tmpdir, rtol=1e-10):
    points = pd.read_hdf(tracks_dir / "track.points")
    IO.save_single_track(points, "track", tmpdir)

    points_test = pd.read_hdf((tmpdir / "track.points"))
    np.testing.assert_allclose(points, points_test, rtol=rtol)


def test_export_single_spline(tmpdir):
    IO.export_single_spline(spline, "track", tmpdir, ATLAS_RESOLUTION)

    spline_test = np.load(str(tmpdir / "track.npy"))
    spline_validate = np.load(str(tracks_dir / "track.npy"))

    assert (spline_test == spline_validate).all()
