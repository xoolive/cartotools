from cartopy.crs import Globe, Projection
from shapely import geometry


class HotineObliqueMercator(Projection):
    def __init__(
        self,
        central_longitude,
        central_latitude,
        scale_factor,
        false_easting,
        false_northing,
        globe,
    ):
        proj4_params = [
            ("proj", "somerc"),
            ("lon_0", central_longitude),
            ("lat_0", central_latitude),
            ("k_0", scale_factor),
            ("x_0", false_easting),
            ("y_0", false_northing),
            ("units", "m"),
        ]
        super(HotineObliqueMercator, self).__init__(proj4_params, globe=globe)

    @property
    def threshold(self):
        return 1e4

    @property
    def boundary(self):
        x0, x1 = self.x_limits
        y0, y1 = self.y_limits
        return geometry.LineString(
            [(x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)]
        )


class CH1903(HotineObliqueMercator):
    """
    Swiss CH1903 / LV03 for Switzerland and Liechtenstein
    Ellipsoid is Bessel.
    """

    def __init__(self):
        globe = Globe(ellipse="bessel")
        super(CH1903, self).__init__(
            central_longitude=7.439583333333333,
            central_latitude=46.95240555555556,
            scale_factor=1,
            false_easting=600000,
            false_northing=200000,
            globe=globe,
        )

    @property
    def x_limits(self):
        return (480000, 850000)

    @property
    def y_limits(self):
        return (70000, 300000)


class CH1903p(HotineObliqueMercator):
    """
    Swiss CH1903+ / LV95 for Switzerland and Liechtenstein
    Ellipsoid is Bessel.
    """

    def __init__(self):
        globe = Globe(ellipse="bessel")
        super(CH1903p, self).__init__(
            central_longitude=7.439583333333333,
            central_latitude=46.95240555555556,
            scale_factor=1,
            false_easting=2600000,
            false_northing=1200000,
            globe=globe,
        )

    @property
    def x_limits(self):
        return (2480000, 2850000)

    @property
    def y_limits(self):
        return (1070000, 1300000)
