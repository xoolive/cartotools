import time
from functools import lru_cache, partial
from typing import Tuple

from shapely.ops import transform


class ShapelyMixin(object):
    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        # just natural!
        # TODO put self.shape somewhere
        return self.shape.bounds  # type: ignore

    @property
    def extent(self) -> Tuple[float, float, float, float]:
        # convenient for ax.set_extent
        west, south, east, north = self.bounds
        return west, east, south, north

    @property
    def _geom(self):
        # convenient for cascaded_union
        return self.shape._geom

    @property
    def type(self):
        # convenient for intersections, etc.
        return self.shape.type

    def _repr_html_(self):
        no_wrap_div = '<div style="white-space: nowrap">{}</div>'
        return no_wrap_div.format(self._repr_svg_())

    def _repr_svg_(self):
        return self.project_shape()._repr_svg_()

    @lru_cache()
    def project_shape(self, projection=None):
        import pyproj  # leave it as optional import

        if projection is None:
            bounds = self.bounds
            projection = pyproj.Proj(
                proj="aea",  # equivalent projection
                lat1=bounds[1],
                lat2=bounds[3],
                lon1=bounds[0],
                lon2=bounds[2],
            )
        return transform(
            partial(
                pyproj.transform, pyproj.Proj(init="EPSG:4326"), projection
            ),
            self.shape,
        )

    def plot(self, ax, **kwargs):

        if "projection" not in ax.__dict__:
            raise ValueError("Specify a projection for your plot")

        if "facecolor" not in kwargs:
            kwargs["facecolor"] = "None"

        if "edgecolor" not in kwargs and "color" in kwargs:
            kwargs["edgecolor"] = kwargs["color"]
            del kwargs["color"]
        elif "edgecolor" not in kwargs:
            kwargs["edgecolor"] = "#aaaaaa"

        if "crs" not in kwargs:
            from cartopy.crs import PlateCarree

            kwargs["crs"] = PlateCarree()

        ax.add_geometries(self, **kwargs)


def json_request(url, timeout=180, **kwargs):
    """
    Send a request to the Overpass API via HTTP POST and return the JSON
    response.

    Reference: https://github.com/gboeing/osmnx/blob/master/osmnx/core.py
    """
    from .. import session

    response = session.post(url, timeout=timeout, **kwargs)

    try:
        response_json = response.json()
    except Exception:
        # 429 is 'too many requests' and 504 is 'gateway timeout' from server
        # overload - handle these errors by recursively calling
        # overpass_request until we get a valid response
        if response.status_code in [429, 504]:
            # pause for error_pause_duration seconds before re-trying request
            time.sleep(1)
            response_json = json_request(url, timeout=timeout, **kwargs)

        # else, this was an unhandled status_code, throw an exception
        else:
            raise Exception(
                "Server returned no JSON data.\n{} {}\n{}".format(
                    response, response.reason, response.text
                )
            )

    return response_json
