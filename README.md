[![Python Version](https://img.shields.io/pypi/pyversions/brainreg-segment.svg)](https://pypi.org/project/brainreg-segment)
[![PyPI](https://img.shields.io/pypi/v/brainreg-segment.svg)](https://pypi.org/project/brainreg-segment)
[![Wheel](https://img.shields.io/pypi/wheel/brainreg-segment.svg)](https://pypi.org/project/brainreg-segment)
[![Development Status](https://img.shields.io/pypi/status/brainreg-segment.svg)](https://github.com/brainglobe/brainreg-segment)
[![Tests](https://img.shields.io/github/workflow/status/brainglobe/brainreg-segment/tests)](
    https://github.com/brainglobe/brainreg-segment/actions)
[![codecov](https://codecov.io/gh/brainglobe/brainreg-segment/branch/master/graph/badge.svg?token=WP9KTPZE5R)](https://codecov.io/gh/brainglobe/brainreg-segment)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![Twitter](https://img.shields.io/twitter/follow/brain_globe?style=social)](https://twitter.com/brain_globe)

# brainreg-segment
Segmentation of 1/2/3D brain structures in a common anatomical space

`brainreg-segment` is a companion to [`brainreg`](https://github.com/brainglobe/brainreg) allowing manual segmentation of regions/objects within the brain (e.g. injection sites, probes etc.) allowing for automated analysis of brain region distribution, and visualisation (e.g. in [brainrender](https://github.com/brainglobe/brainrender)).

`brainreg-segment` and `brainreg` were developed by [Adam Tyson](https://github.com/adamltyson) and [Charly Rousseau](https://github.com/crousseau) in the [Margrie Lab](https://www.sainsburywellcome.org/web/groups/margrie-lab), based on [aMAP](https://doi.org/10.1038/ncomms11879) by [Christian Niedworok](https://github.com/cniedwor). The work was generously supported by the [Sainsbury Wellcome Centre](https://www.sainsburywellcome.org/web/).

## Installation

brainreg-segment comes bundled with [`brainreg`](https://github.com/brainglobe/brainreg), so see the [brainreg installation instructions](https://brainglobe.info/documentation/brainreg/index.html).

brainreg-segment can be installed on it's own (`pip install brainreg-segment`), but you will need to register your data with brainreg first.

## Usage

See [user guide](https://brainglobe.info/documentation/brainreg-segment/index.html).

If you have any questions, head over to the [image.sc forum](https://forum.image.sc/tag/brainglobe).

## Contributing
Contributions are very welcome. Please see the [developers guide](https://brainglobe.info/developers/index.html).

### Citing brainreg-segment

If you find brainreg-segment useful, and use it in your research, please let us know and also cite the paper:

> Tyson, A. L., V&eacute;lez-Fort, M.,  Rousseau, C. V., Cossell, L., Tsitoura, C., Lenzi, S. C., Obenhaus, H. A., Claudi, F., Branco, T.,  Margrie, T. W. (2022). Accurate determination of marker location within whole-brain microscopy images. Scientific Reports, 12, 867 [doi.org/10.1038/s41598-021-04676-9](https://doi.org/10.1038/s41598-021-04676-9)
