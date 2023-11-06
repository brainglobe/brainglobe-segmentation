from importlib.metadata import PackageNotFoundError, version
from . import *

__author__ = "Adam Tyson"

try:
    __version__ = version("brainreg-segment")
except PackageNotFoundError:
    # package is not installed
    pass
