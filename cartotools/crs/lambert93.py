from cartopy.crs import Globe, LambertConformal
from shapely import geometry


class Lambert93(LambertConformal):
    """
    Lambert Conformal projection for France (IGN).
    Ellipsoid is WGS84.
    """

    def __init__(self):
        globe = Globe(ellipse="GRS80")
        super(Lambert93, self).__init__(
            3,
            46.5,
            standard_parallels=(44, 49),
            false_easting=700000,
            false_northing=6600000,
            globe=globe,
        )

    @property
    def x_limits(self):
        return (0, 1300000)

    @property
    def y_limits(self):
        return (5900000, 7200000)

    @property
    def boundary(self):
        x0, x1 = self.x_limits
        y0, y1 = self.y_limits
        return geometry.LineString(
            [(x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)]
        )
