import numpy as np
import pytest
from pandas import read_csv

from brainreg_segment.tracks.analysis import analyse_track_anatomy, spline_fit


@pytest.fixture
def pts_2d():
    return np.array([[13, 48], [18, 45], [17, 47], [17, 48], [17, 49]])


@pytest.fixture
def pts_3d():
    return np.array(
        [
            [140, 117, 148],
            [155, 118, 145],
            [168, 118, 147],
            [171, 119, 148],
            [184, 119, 149],
        ]
    )


@pytest.fixture
def fit_2d():
    return np.array(
        [
            [13.0007243, 47.99991222],
            [15.66567757, 45.97351346],
            [17.30088783, 44.76737589],
            [18.1101873, 44.25892636],
            [18.29740821, 44.32559171],
            [18.06638278, 44.84479877],
            [17.62094322, 45.69397439],
            [17.16492177, 46.75054541],
            [16.90215064, 47.89193866],
            [17.03646205, 48.99558099],
        ]
    )


@pytest.fixture
def fit_3d():
    return np.array(
        [
            [139.99573018, 117.0151013, 148.00538332],
            [144.90082934, 117.33988256, 145.95966354],
            [149.78383806, 117.62840082, 145.01974771],
            [154.65242553, 117.88542582, 144.9428862],
            [159.51426093, 118.11572727, 145.48632939],
            [164.37701345, 118.32407492, 146.40732764],
            [169.24835227, 118.51523848, 147.46313133],
            [174.13594657, 118.69398769, 148.41099081],
            [179.04746554, 118.86509228, 149.00815646],
            [183.99057836, 119.03332197, 149.01187864],
        ]
    )


def test_fit(pts_2d, pts_3d, fit_2d, fit_3d, rtol=1e-5):
    np.testing.assert_allclose(
        spline_fit(pts_2d, n_points=10), fit_2d, rtol=rtol
    )
    np.testing.assert_allclose(
        spline_fit(pts_3d, n_points=10), fit_3d, rtol=rtol
    )


def test_analyse_track_anatomy(fit_3d, allen_mouse_50um_atlas, tmp_path):
    atlas = allen_mouse_50um_atlas
    output_file = tmp_path / "2d_analysis.csv"
    analyse_track_anatomy(atlas.annotation, atlas, fit_3d, output_file)

    df = read_csv(output_file)
    assert df["Region name"][0] == "internal capsule"
    assert df["Region name"][4] == "cerebal peduncle"
    assert df["Region name"][5] == "root"
    assert df["Region name"][6] == "Not found in brain"
