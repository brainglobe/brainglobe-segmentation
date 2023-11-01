import warnings

warnings.warn(
    "brainreg-segment is deprecated. Please use brainglobe-segmentation instead: https://github.com/brainglobe/brainglobe-segmentation",
    DeprecationWarning,
)

from importlib.metadata import PackageNotFoundError, version
from . import *

__author__ = "Adam Tyson"

try:
    __version__ = version("brainreg-segment")
except PackageNotFoundError:
    # package is not installed
    pass
