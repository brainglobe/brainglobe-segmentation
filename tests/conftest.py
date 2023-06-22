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


@pytest.fixture
def segmentation_widget_with_data_sample_space(segmentation_widget):
    return load_brainreg_dir(segmentation_widget, standard_space=False)


@pytest.fixture
def segmentation_widget_with_data_atlas_space(segmentation_widget):
    return load_brainreg_dir(segmentation_widget, standard_space=True)


def load_brainreg_dir(segmentation_widget, standard_space=False):
    segmentation_widget.standard_space = standard_space
    segmentation_widget.plugin = "brainglobe-napari-io.brainreg_read_dir"
    segmentation_widget.directory = brainreg_dir
    segmentation_widget.load_brainreg_directory()
    return segmentation_widget
