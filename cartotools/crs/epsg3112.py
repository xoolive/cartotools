from cartopy.crs import Globe, LambertConformal
from shapely import geometry


class GeoscienceAustraliaLambert(LambertConformal):
    """
    Geoscience Australia Lambert, EPSG 3112
    https://epsg.io/3112
    """

    def __init__(self):
        globe = Globe(ellipse="GRS80")
        super().__init__(
            134,
            0,
            standard_parallels=(-18, -36),
            false_easting=0,
            false_northing=0,
            globe=globe,
        )

    @property
    def x_limits(self):
        return (-3000000, 4500000)

    @property
    def y_limits(self):
        return (-6000000, 0)

    @property
    def boundary(self):
        x0, x1 = self.x_limits
        y0, y1 = self.y_limits
        return geometry.LineString(
            [(x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)]
        )
