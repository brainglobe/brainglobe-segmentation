import shutil
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
    Create a viewer, add the segmentation widget, and return the widget.
    The viewer can be accessed using ``widget.viewer``.
    """
    viewer = make_napari_viewer()
    widget = SegmentationWidget(viewer)
    viewer.window.add_dock_widget(widget)
    return widget


@pytest.fixture(scope="function")
def segmentation_widget_with_data_atlas_space(tmp_path, segmentation_widget):
    """
    Fixture to load a brainreg directory into the segmentation widget.
    Data is copied to tmpdir so that when it's loaded, so all the paths
    are set correctly.
    The manual segmentation data is then deleted so that saving/export
    can be properly tested
    """
    tmp_input_dir = tmp_path / "brainreg_output"
    shutil.copytree(brainreg_dir, tmp_input_dir)
    segmentation_widget.standard_space = True
    segmentation_widget.plugin = (
        "brainglobe-napari-io.brainreg_read_dir_standard_space"
    )
    segmentation_widget.directory = Path(tmp_input_dir)
    segmentation_widget.load_brainreg_directory()
    # delete manual segmentation data to ensure it's saved correctly in tests
    shutil.rmtree(segmentation_widget.paths.main_directory)
    return segmentation_widget
