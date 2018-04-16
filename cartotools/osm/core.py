from functools import partial
from typing import Tuple

import requests
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

    def __repr__(self):
        return "{}: {}".format(__class__.__name__, self.display_name)

    def _repr_svg_(self):
        print(self.display_name)
        try:
            type(self.proj_shape)
        except AttributeError:
            self.proj_shape = None
        if self.proj_shape is None:
            try:
                self.shape_project()
            except ImportError:
                pass
        return self.proj_shape._repr_svg_()

    def shape_project(self, projection=None):
        import pyproj  # leave it as optional import
        if projection is None:
            bounds = self.bounds
            projection = pyproj.Proj(proj='aea',  # equivalent projection
                                     lat1=bounds[1], lat2=bounds[3],
                                     lon1=bounds[0], lon2=bounds[2])
        self.proj_shape = transform(
            partial(pyproj.transform, pyproj.Proj(init='EPSG:4326'),
                    projection),
            self.shape)

    def plot(self, ax, **kwargs):

        if not 'projection' in ax.__dict__:
            raise ValueError("Specify a projection for your plot")

        if 'facecolor' not in kwargs:
            kwargs['facecolor'] = 'None'

        if 'edgecolor' not in kwargs and 'color' in kwargs:
            kwargs['edgecolor'] = kwargs['color']
            del kwargs['color']
        elif 'edgecolor' not in kwargs:
            kwargs['edgecolor'] = '#aaaaaa'

        if 'crs' not in kwargs:
            from cartopy.crs import PlateCarree
            kwargs['crs'] = PlateCarree()

        ax.add_geometries(self, **kwargs)


def json_request(url, timeout=180, **kwargs):
    """
    Send a request to the Overpass API via HTTP POST and return the JSON
    response.
    Parameters
    ----------
    data : dict or OrderedDict
        key-value pairs of parameters to post to the API
    timeout : int
        the timeout interval for the requests library
    Returns
    -------
    dict

    Reference: https://github.com/gboeing/osmnx/blob/master/osmnx/core.py
    """

    response = requests.post(url, timeout=timeout, **kwargs)

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
            raise Exception('Server returned no JSON data.\n{} {}\n{}'.format(
                response, response.reason, response.text))

    return response_json

