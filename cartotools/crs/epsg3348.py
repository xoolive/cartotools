from cartopy.crs import Globe, LambertConformal
from shapely import geometry


class StatisticsCanadaLambert(LambertConformal):
    """
    Statistics Canada Lambert, EPSG 3348
    https://epsg.io/3348
    """

    def __init__(self):
        globe = Globe(ellipse="GRS80")
        super().__init__(
            -91.866666,
            63.390675,
            standard_parallels=(49, 77),
            false_easting=6_200_000,
            false_northing=3_000_000,
            globe=globe,
        )

    @property
    def x_limits(self):
        return (3_000_000, 9_000_000)

    @property
    def y_limits(self):
        return (500_000, 5_000_000)

    @property
    def boundary(self):
        x0, x1 = self.x_limits
        y0, y1 = self.y_limits
        return geometry.LineString(
            [(x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)]
        )
