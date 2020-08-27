from brainreg_segment.segment import start_gui


def test_gui(make_test_viewer):
    viewer = make_test_viewer()
    start_gui(viewer)
