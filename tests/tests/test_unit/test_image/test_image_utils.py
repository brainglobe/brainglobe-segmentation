import numpy as np

from brainreg_segment.image.utils import create_KDTree_from_image

image = np.array(
    (
        [0, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
    )
)

data_0 = np.array(
    [
        [0.0, 0.0],
        [0.0, 1.0],
        [0.0, 2.0],
        [0.0, 3.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [1.0, 3.0],
        [2.0, 0.0],
        [2.0, 3.0],
        [3.0, 0.0],
        [3.0, 1.0],
        [3.0, 2.0],
        [3.0, 3.0],
    ]
)

data_1 = np.array([[1.0, 2.0], [2.0, 1.0], [2.0, 2.0]])


def test_create_KDTree_from_image():
    tree = create_KDTree_from_image(image)
    assert (tree.data == data_0).all()

    tree = create_KDTree_from_image(image, value=1)
    assert (tree.data == data_1).all()
