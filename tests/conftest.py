# COPIED FROM NAPARI - how to import?

import warnings
from typing import List

import pytest
from napari import Viewer
from qtpy.QtWidgets import QApplication


def pytest_addoption(parser):
    """Add napari specific command line options.

    --show-viewer
        Show viewers during tests, they are hidden by default. Showing viewers
        decreases test speed by around 20%.

    --perfmon-only
        Run only perfmon test.

    Notes
    -----
    Due to the placement of this conftest.py file, you must specifically name
    the napari folder such as "pytest napari --show-viewer"

    For --perfmon-only must also enable perfmon with env var:
    NAPARI_PERFMON=1 pytest napari --perfmon-only
    """
    parser.addoption(
        "--show-viewer",
        action="store_true",
        default=False,
        help="don't show viewer during tests",
    )

    parser.addoption(
        "--perfmon-only",
        action="store_true",
        default=False,
        help="run only perfmon tests",
    )


@pytest.fixture
def qtbot(qtbot):
    """A modified qtbot fixture that makes sure no widgets have been leaked."""
    initial = QApplication.topLevelWidgets()
    yield qtbot
    QApplication.processEvents()
    leaks = set(QApplication.topLevelWidgets()).difference(initial)
    # still not sure how to clean up some of the remaining vispy
    # vispy.app.backends._qt.CanvasBackendDesktop widgets...
    # if any([n.__class__.__name__ != "CanvasBackendDesktop" for n in leaks]):
    #    raise AssertionError(f"Widgets leaked!: {leaks}")
    if leaks:
        warnings.warn(f"Widgets leaked!: {leaks}")


@pytest.fixture(scope="function")
def make_test_viewer(qtbot, request):
    viewers: List[Viewer] = []

    def actual_factory(*model_args, **model_kwargs):
        model_kwargs["show"] = model_kwargs.pop(
            "show", request.config.getoption("--show-viewer")
        )
        viewer = Viewer(*model_args, **model_kwargs)
        viewers.append(viewer)
        return viewer

    yield actual_factory

    for viewer in viewers:
        viewer.close()
