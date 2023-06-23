from pathlib import Path

import pytest
from bg_atlasapi import BrainGlobeAtlas

from brainreg_segment.segment import SegmentationWidget

atlas_name = "allen_mouse_50um"
brainreg_dir = Path.cwd() / "tests" / "data" / "brainreg_output"


@pytest.fixture
def allen_mouse_50um_atlas():
    return BrainGlobeAtlas(atlas_name)


@pytest.fixture
def segmentation_widget(make_napari_viewer):
    """
    Create a viewer, add the curation widget, and return the widget.
    The viewer can be accessed using ``widget.viewer``.
    """
    viewer = make_napari_viewer()
    widget = SegmentationWidget(viewer)
    viewer.window.add_dock_widget(widget)
    return widget
