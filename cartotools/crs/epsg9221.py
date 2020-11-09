from cartopy.crs import Globe, LambertConformal
from shapely import geometry


class Hartebeesthoek94(LambertConformal):
    """
    Haartebeesthoek 94 for South Africa, EPSG 9221

    https://epsg.io/9221
    """

    def __init__(self):
        globe = Globe(ellipse="GRS80")
        super().__init__(
            25,
            -30,  # 25,
            standard_parallels=(-22, -38),
            false_easting=1_400_000,
            false_northing=130_000,
            globe=globe,
        )

    @property
    def x_limits(self):
        return (-500_000, 2_500_000)

    @property
    def y_limits(self):
        return (-1_000_000, 1_500_000)

    @property
    def boundary(self):
        x0, x1 = self.x_limits
        y0, y1 = self.y_limits
        return geometry.LineString(
            [(x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)]
        )
