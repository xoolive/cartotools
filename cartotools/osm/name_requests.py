from collections import OrderedDict, UserDict
from functools import partial
from typing import Any, Dict, List, NamedTuple

from shapely.geometry import shape
from shapely.ops import transform

from .core import json_request

__all__ = ['location']

boundingbox = NamedTuple("boundingbox", [('west', float), ('east', float),
                                         ('south', float), ('north', float)])


def name_request(query: str):

    params: Dict['str', Any] = OrderedDict()

    params['format'] = 'json'
    params['limit'] = 1
    params['dedupe'] = 0  # this prevents OSM from de-duping results
    # so we're guaranteed to get precisely 'limit' number of results
    params['polygon_geojson'] = 1

    if isinstance(query, str):
        params['q'] = query
    elif isinstance(query, dict):
        # add the query keys in alphabetical order so the URL is the same
        # string each time, for caching purposes
        for key in sorted(list(query.keys())):
            params[key] = query[key]

    url = 'https://nominatim.openstreetmap.org/search'
    return json_request(url, timeout=30, params=params)


class NameRequest(object):

    def __init__(self, name: str) -> None:
        results: List[Dict[str, Any]] = name_request(name)
        if len(results) == 0:
            raise ValueError(f"No '{name}' found on OpenStreetMap")
        json = results[0]
        self.display_name = json['display_name']
        self.bbox = boundingbox(south=float(json['boundingbox'][0]),
                                north=float(json['boundingbox'][1]),
                                west=float(json['boundingbox'][2]),
                                east=float(json['boundingbox'][3]))
        self.shape = shape(json['geojson'])
        self.proj_shape = None

    def _repr_svg_(self):
        print(self.display_name)
        if self.proj_shape is None:
            self.shape_project()
        return self.proj_shape._repr_svg_()

    def shape_project(self, projection=None):
        import pyproj  # leave it as optional import
        if projection is None:
            projection = pyproj.Proj(proj='aea',  # equivalent projection
                                     lat1=self.shape.bounds[1],
                                     lat2=self.shape.bounds[3],
                                     lon1=self.shape.bounds[0],
                                     lon2=self.shape.bounds[2])
        self.proj_shape = transform(
            partial(pyproj.transform, pyproj.Proj(init='EPSG:4326'),
                    projection),
            self.shape)


class CacheRequests(UserDict):
    def __missing__(self, name: str):
        lower = name.lower()
        if lower in self:
            return self[lower]
        result = NameRequest(name)
        self[lower] = result
        return result


location = CacheRequests()
location._ipython_key_completions_ = location.keys()  # type: ignore
