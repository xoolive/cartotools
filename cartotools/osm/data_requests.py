import hashlib
import json
from collections import UserDict
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests
from shapely.geometry import LineString, Polygon, Point
from shapely.ops import cascaded_union

from .core import json_request
from .name_requests import NameRequest

__all__ = ['request']


class Response(object):

    def __init__(self, response: Dict[str, Any]) -> None:
        self.response = response
        self.nodes = {p['id']: p for p in self.response['elements']
                      if p['type'] == 'node'}
        self.ways = {p['id']: (p, LineString(list((self.nodes[node]['lon'],
                                                   self.nodes[node]['lat']))
                                             for node in p['nodes']))
                     for p in self.response['elements']
                     if p['type'] == 'way'}
        # todo improve this shit
        self.ways = {key: (value, (Polygon(shape) if shape.is_closed else shape))
                     for (key, (value, shape)) in self.ways.items()}
        
    def geometry(self):
        if len(self.ways) > 0:
            return cascaded_union([p[1] for p in self.ways.values()])
        return cascaded_union([Point(p['lon'], p['lat'])
                               for p in self.nodes.values()])
    
    @property
    def shape(self):
        return self.geometry()
    
    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        return self.shape.bounds
    
    @property
    def extent(self) -> Tuple[float, float, float, float]:
        west, south, east, north = self.bounds
        return west, east, south, north
        
    @property
    def _geom(self):
        return self.shape._geom
    
    @property
    def type(self):
        return self.shape.type
    
    def __iter__(self):
        if len(self.ways) > 0:
            for p in self.ways.values():
                yield p[1]
            return
        for p in self.point.values():
            yield Point(p['lon'], p['lat'])
            
    def subset(rep, **kwargs):
        for key, (meta, shape) in rep.ways.items():
            for k, v in kwargs.items():
                if k in meta['tags'] and meta['tags'][k] == v:
                    yield key, (meta, shape)
                    
    def keys(rep):
        keys = set()
        for meta, shape in rep.ways.values():
            for key in meta['tags'].keys():
                keys.add(key)

        return keys
    
    def values(rep, k):
        values = set()
        for meta, shape in rep.ways.values():
            for key in meta['tags'].keys():
                if key == k:
                    values.add(meta['tags'][key])
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
            response = Response(json.loads(filename.read_text()))
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
             '({south:.8f},{west:.8f},{north:.8f},{east:.8f});>;);out {meta};')

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

    def json_request(self, within: Optional[NameRequest]=None,
                     **kwargs) -> Response:

        query_str = self.get_query('json', within, meta="", **kwargs)
        
        hashcode = hashlib.md5(query_str.encode('utf-8')).hexdigest()
        response = self.cache.get(hashcode, None)
        if response is not None:
            return self.cache[hashcode]

        response = requests.post(url=self.url, data=query_str)
        response = Response(response.json())
        self.cache[hashcode] = response
        return response

    def xml_request(self, within: Optional[NameRequest]=None,
                    **kwargs) -> str:

        query_str = self.get_query('xml', within, meta="meta", **kwargs)

        data = {'data': query_str}
        response = requests.post(self.url, **data)
        return response.content.decode('utf8')
    
    def __call__(self, within: Optional[NameRequest]=None,
                 **kwargs) -> Response:
        return self.json_request(within, **kwargs)


request = DataRequests()
