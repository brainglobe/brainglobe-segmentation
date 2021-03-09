from setuptools import setup, find_namespace_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

requirements = [
    "numpy",
    "scikit-image",
    "pandas",
    "napari[pyside2]>=0.3.7",
    "imlib >= 0.0.26",
    "dask >= 2.15.0",
    "napari-brainreg",
    "imio",
]


setup(
    name="brainreg-segment",
    version="0.2.3",
    description="Manual segmentation of 3D brain structures in a common anatomical space",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black",
            "pytest-cov",
            "pytest",
            "pytest-qt",
            "coverage",
            "bump2version",
            "pre-commit",
            "flake8",
        ]
    },
    python_requires=">=3.7",
    packages=find_namespace_packages(exclude=("docs", "tests*")),
    entry_points={
        "console_scripts": [
            "brainreg_segment = brainreg_segment.segment:main",
        ]
    },
    include_package_data=True,
    author="Adam Tyson, Horst Obenhaus",
    author_email="adam.tyson@ucl.ac.uk",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
    zip_safe=False,
)
