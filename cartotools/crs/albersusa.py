from cartopy.crs import AlbersEqualArea, Globe


class AlbersUSA(AlbersEqualArea):
    def __init__(self):
        globe = Globe(datum="NAD83")
        super().__init__(
            central_longitude=-96,
            central_latitude=23,
            standard_parallels=(29.5, 45.5),
            globe=globe,
        )

    @property
    def x_limits(self):
        return (-2_500_000, 2_500_000)

    @property
    def y_limits(self):
        return (0, 5_000_000)
