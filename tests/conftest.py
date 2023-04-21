import pytest
from bg_atlasapi import BrainGlobeAtlas

atlas_name = "allen_mouse_50um"


@pytest.fixture
def allen_mouse_50um_atlas():
    return BrainGlobeAtlas(atlas_name)
