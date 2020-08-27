from pathlib import Path
from brainreg_segment.segment import SegmentationWidget

brainreg_dir = Path.cwd() / "tests" / "data" / "brainreg_output"


def test_load_sample_space(make_test_viewer):
    viewer = make_test_viewer()
    widget = SegmentationWidget(viewer)
    viewer.window.add_dock_widget(widget, name="General", area="right")
    widget.standard_space = False
    widget.plugin = "brainreg"
    widget.directory = brainreg_dir
    widget.load_brainreg_directory()
    check_loaded_layers(widget)


def test_load_atlas_space(make_test_viewer):
    viewer = make_test_viewer()
    widget = SegmentationWidget(viewer)
    viewer.window.add_dock_widget(widget, name="General", area="right")
    widget.standard_space = True
    widget.plugin = "brainreg_standard"
    widget.directory = brainreg_dir
    widget.load_brainreg_directory()
    check_loaded_layers(widget)


def check_loaded_layers(widget):
    assert len(widget.viewer.layers) == 2
    assert widget.base_layer.name == "Registered image"
    assert widget.atlas.atlas_name == "allen_mouse_50um"
    assert widget.metadata["orientation"] == "psl"
    assert widget.atlas_layer.name == widget.atlas.atlas_name


def test_general(make_test_viewer):
    viewer = make_test_viewer()
    widget = SegmentationWidget(viewer)
    viewer.window.add_dock_widget(widget, name="General", area="right")
    widget.standard_space = True
    widget.plugin = "brainreg_standard"
    widget.directory = brainreg_dir
    widget.load_brainreg_directory()

    assert (
        widget.paths.segmentation_directory
        == brainreg_dir / "manual_segmentation" / "standard_space"
    )
