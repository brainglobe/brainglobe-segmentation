from filecmp import cmp
from pathlib import Path

import tifffile

from brainreg_segment.regions import IO as region_IO

regions_dir = Path.cwd() / "tests" / "data" / "regions"
VOXEL_SIZE = 100


def test_export_regions_to_file(tmp_path):
    image = tifffile.imread(regions_dir / "region.tiff")
    filename = tmp_path / "region.obj"
    region_IO.export_regions_to_file(image, filename, VOXEL_SIZE)

    cmp(regions_dir / "region.obj", tmp_path / "region.obj")
