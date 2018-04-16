import hashlib
import json
from collections import UserDict
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Set, Tuple, Union

import requests
from shapely.geometry import LineString, Point, Polygon, base
from shapely.ops import cascaded_union

from .core import ShapelyMixin, json_request
from .name_requests import NameRequest, location

__all__ = ['request']


class Response(ShapelyMixin):

    def __init__(self, response: Dict[str, Any], name: str) -> None:

        self.response = response

        self.nodes = {p['id']: p for p in self.response['elements']
                      if p['type'] == 'node'}

        self.ways = {p['id']: (p, LineString(list((self.nodes[node]['lon'],
                                                   self.nodes[node]['lat']))
                                             for node in p['nodes']))
                     for p in self.response['elements']
                     if p['type'] == 'way'}

        # TODO improve this shit
        self.ways = {key: (value, (Polygon(shape)
                                   if shape.is_closed else shape))
                     for (key, (value, shape)) in self.ways.items()}

        self.relations = {p['id']: p for p in self.response['elements']
                          if p['type'] == 'relation'}

        self.display_name: str = name  # TODO

    @property
    def shape(self) -> base.BaseGeometry:
        return cascaded_union(list(self))

    def __iter__(self):
        if len(self.ways) > 0:
            for p in self.ways.values():
                yield p[1]
            return
        for p in self.nodes.values():
            yield Point(p['lon'], p['lat'])

    def subset(self, **kwargs) -> Iterator[
            Tuple[str, Tuple[Dict, base.BaseGeometry]]]:
        for key, (meta, shape) in self.ways.items():
            for k, v in kwargs.items():
                if k in meta['tags'] and meta['tags'][k] == v:
                    yield key, (meta, shape)

    def keys(self) -> Set[str]:
        keys = set()
        for meta, shape in self.ways.values():
            for key in meta['tags'].keys():
                keys.add(key)
        return keys

    def values(self, key: str) -> Set[str]:
        values = set()
        for meta, shape in self.ways.values():
            for key_ in meta['tags'].keys():
                if key_ == key:
                    values.add(meta['tags'][key_])
        return values


class OSMCache(UserDict):

    def __init__(self, cachedir="./cache"):
        self.cachedir = Path(cachedir)
        if not self.cachedir.exists():
            self.cachedir.mkdir(parents=True)
        super().__init__()

    def __missing__(self, hashcode: str):
        filename = self.cachedir / f"{hashcode}.json"
        if filename.exists():
            response = Response(json.loads(filename.read_text()), hashcode)
            # Attention à ne pas réécrire le fichier...
            super().__setitem__(hashcode, response)
            return response

    def __setitem__(self, hashcode: str, data):
        super().__setitem__(hashcode, data)
        filename = self.cachedir / f"{hashcode}.json"
        with filename.open('w') as fh:
            fh.write(json.dumps(data.response))


class DataRequests(object):

    query = ('[out:{format}][timeout:{timeout}]{maxsize};'
             '({infrastructure}{filters}'
             '({south:.8f},{west:.8f},{north:.8f},{east:.8f});>;);'
             'out {meta};')

    url = 'http://www.overpass-api.de/api/interpreter'

    cache: Dict['str', Any] = OSMCache()

    def get_query(self, format_: str, within: Optional[NameRequest]=None,
                  **kwargs) -> str:

        if within is not None:
            kwargs = {**kwargs, **within.bbox._asdict()}

        if 'maxsize' not in kwargs:
            kwargs['maxsize'] = ''

        if 'timeout' not in kwargs:
            kwargs['timeout'] = 180

        kwargs['format'] = format_
        query_str = self.query.format(**kwargs)

        return query_str

    def json_request(self, within: Optional[Union[str, NameRequest]]=None,
                     requests_extra: Dict[str, str] = dict(),
                     **kwargs) -> Response:

        if isinstance(within, str):
            within = location(within)

        infrastructure = kwargs['infrastructure']
        del kwargs['infrastructure']

        filters = ''
        for key, value in kwargs.items():
            if value is None:
                filters += '["{}"]'.format(key)
            else:
                filters += '["{}"~"{}"]'.format(key, value)

        query_str = self.get_query(format_='json',
                                   within=within,
                                   meta="",
                                   infrastructure=infrastructure,
                                   filters=filters)

        hashcode = hashlib.md5(query_str.encode('utf-8')).hexdigest()
        response = self.cache.get(hashcode, None)
        if response is not None:
            return self.cache[hashcode]

        response = requests.post(url=self.url, data=query_str,
                                 **requests_extra)
        response = Response(response.json(), hashcode)
        self.cache[hashcode] = response
        return response

    def xml_request(self, within: Optional[NameRequest]=None,
                    **kwargs) -> str:

        query_str = self.get_query('xml', within, meta="meta", **kwargs)

        data = {'data': query_str}
        response = requests.post(self.url, **data)
        return response.content.decode('utf8')

    # more natural than a subsequent call to json_request!
    def __call__(self, within: Optional[NameRequest]=None,
                 **kwargs) -> Response:
        return self.json_request(within, **kwargs)


request = DataRequests()
