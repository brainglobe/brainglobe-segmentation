class Paths:
    """
    A single class to hold all file paths that may be used.
    """

    def __init__(
        self, brainreg_directory, standard_space=True, atlas_space=False
    ):
        self.brainreg_directory = brainreg_directory
        self.main_directory = self.brainreg_directory / "manual_segmentation"

        if atlas_space:
            self.segmentation_directory = self.main_directory / "atlas_space"
        else:
            if standard_space:
                self.segmentation_directory = (
                    self.main_directory / "standard_space"
                )
            else:
                self.segmentation_directory = (
                    self.main_directory / "sample_space"
                )

        self.regions_directory = self.join_seg_files("regions")
        self.region_summary_csv = self.regions_directory / "summary.csv"

        self.tracks_directory = self.join_seg_files("tracks")

    def join_seg_files(self, filename):
        return self.segmentation_directory / filename
