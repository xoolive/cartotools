from collections import OrderedDict, UserDict
from typing import Any, Dict, Iterator, List, NamedTuple

from shapely.geometry import base, shape

from .core import ShapelyMixin, json_request

__all__ = ['location']

boundingbox = NamedTuple("boundingbox", [
    ('west', float), ('east', float), ('south', float), ('north', float)
])


def name_request(query: str, **kwargs):

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
    return json_request(url, timeout=30, params=params, **kwargs)


class NameRequest(ShapelyMixin):

    def __init__(self, name: str, **kwargs) -> None:

        results: List[Dict[str, Any]] = name_request(name, **kwargs)

        if len(results) == 0:
            raise ValueError(f"No '{name}' found on OpenStreetMap")

        json = results[0]
        self.display_name = json['display_name']

        # may look useless but we enjoy the named tuple in data_requests.py
        self.bbox = boundingbox(south=float(json['boundingbox'][0]),
                                north=float(json['boundingbox'][1]),
                                west=float(json['boundingbox'][2]),
                                east=float(json['boundingbox'][3]))

        self.shape = shape(json['geojson'])

        self.proj_shape = None

    def __iter__(self) -> Iterator[base.BaseGeometry]:
        # convenient for cascaded_union
        yield self.shape


class CachedRequests(UserDict):

    kwargs: Dict = dict()

    def __missing__(self, name: str) -> NameRequest:
        lower = name.lower()
        if lower in self:
            return self[lower]
        result = NameRequest(name, **self.kwargs)
        self[lower] = result
        return result

    # a round bracket call is more natural!
    def __call__(self, name: str) -> NameRequest:
        return self[name]


location = CachedRequests()
location._ipython_key_completions_ = location.keys()  # type: ignore
