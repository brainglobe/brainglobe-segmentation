from pathlib import Path

import numpy as np
import pandas as pd
from bg_atlasapi import BrainGlobeAtlas

from brainreg_segment.tracks.analysis import run_track_analysis

atlas_name = "allen_mouse_50um"
atlas = BrainGlobeAtlas(atlas_name)

tracks_dir = Path.cwd() / "tests" / "data" / "tracks"

spline_validate = np.array(
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


def test_run_track_analysis(tmpdir, rtol=1e-10):
    points = np.array(pd.read_hdf(tracks_dir / "track.points"))
    spline_test = run_track_analysis(
        points, "track", tmpdir, atlas, spline_points=10
    )

    np.testing.assert_allclose(spline_test, spline_validate, rtol=rtol)

    regions_validate = pd.read_csv(tracks_dir / "track.csv")
    regions_test = pd.read_csv(tmpdir / "track.csv")

    pd.testing.assert_frame_equal(regions_test, regions_validate)
