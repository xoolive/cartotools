from cartopy.crs import Globe, TransverseMercator
from shapely import geometry


class GaussKruger(TransverseMercator):
    """
    Gauss-Kruger projection for Germany.
    Ellipsoid is Bessel 1841.
    https://epsg.io/5680-15949
    """

    def __init__(self):
        globe = Globe(ellipse="bessel")
        super(GaussKruger, self).__init__(
            9,
            0,
            scale_factor=1,
            false_easting=3500000,
            false_northing=0,
            globe=globe,
        )

    @property
    def x_limits(self):
        return (3200000, 4000000)

    @property
    def y_limits(self):
        return (5200000, 6200000)

    @property
    def boundary(self):
        x0, x1 = self.x_limits
        y0, y1 = self.y_limits
        return geometry.LineString(
            [(x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)]
        )
