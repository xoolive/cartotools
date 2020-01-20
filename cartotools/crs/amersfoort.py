from cartopy.crs import Globe, Stereographic
from shapely import geometry


class Amersfoort(Stereographic):
    """
    Amersfoort projection for the Netherlands.
    Ellipsoid is Bessel 1841.
    https://epsg.io/28992
    """

    def __init__(self):
        globe = Globe(ellipse="bessel")
        super(Amersfoort, self).__init__(
            52.15616055555555,
            5.38763888888889,
            false_easting=155000,
            false_northing=463000,
            true_scale_latitude=0.9999079,
            globe=globe,
        )

    @property
    def x_limits(self):
        return (-100000, 330000)

    @property
    def y_limits(self):
        return (150000, 650000)

    @property
    def boundary(self):
        x0, x1 = self.x_limits
        y0, y1 = self.y_limits
        return geometry.LineString(
            [(x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)]
        )
