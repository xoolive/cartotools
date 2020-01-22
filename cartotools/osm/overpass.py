import hashlib
import json
import logging
from collections import UserDict
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Set, Tuple

import pandas as pd
from appdirs import user_cache_dir
from shapely.geometry import LineString, Point, Polygon, base
from shapely.ops import cascaded_union

from .core import ShapelyMixin
from .nominatim import LocationType, Nominatim, location

__all__ = ["request"]


class Response(ShapelyMixin):
    def __init__(self, response: Dict[str, Any], name: str) -> None:

        self.response = response

        self.nodes = {
            p["id"]: p for p in self.response["elements"] if p["type"] == "node"
        }

        self.ways = {
            p["id"]: (
                p,
                LineString(
                    list((self.nodes[node]["lon"], self.nodes[node]["lat"]))
                    for node in p["nodes"]
                ),
            )
            for p in self.response["elements"]
            if p["type"] == "way"
        }

        # TODO improve
        self.ways = {
            key: (value, (Polygon(shape) if shape.is_closed else shape))
            for (key, (value, shape)) in self.ways.items()
        }

        self.relations = {
            p["id"]: p
            for p in self.response["elements"]
            if p["type"] == "relation"
        }

        self.areas = {
            p["id"]: p for p in self.response["elements"] if p["type"] == "area"
        }

        self.display_name: str = name  # TODO improve

    @property
    def shape(self) -> base.BaseGeometry:
        return cascaded_union(list(self))

    def __iter__(self):
        if len(self.ways) > 0:
            for p in self.ways.values():
                yield p[1]
            return
        for p in self.nodes.values():
            yield Point(p["lon"], p["lat"])

    def subset(
        self, **kwargs
    ) -> Iterator[Tuple[str, Tuple[Dict, base.BaseGeometry]]]:
        for key, (meta, shape) in self.ways.items():
            for k, v in kwargs.items():
                if k in meta["tags"] and meta["tags"][k] == v:
                    yield key, (meta, shape)

    def keys(self) -> Set[str]:
        keys = set()
        for meta, _shape in self.ways.values():
            for key in meta["tags"].keys():
                keys.add(key)
        return keys

    def values(self, key: str) -> Set[str]:
        values = set()
        for meta, _shape in self.ways.values():
            for key_ in meta["tags"].keys():
                if key_ == key:
                    values.add(meta["tags"][key_])
        return values

    @property
    def related(self) -> Dict[int, List[Dict]]:
        return {
            key: list(
                elt for elt in rel["members"] if elt["type"] == "relation"
            )
            for key, rel in self.relations.items()
        }


class OSMCache(UserDict):
    def __init__(self):
        self.cachedir = Path(user_cache_dir("cartotools")) / "json"
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
        with filename.open("w") as fh:
            fh.write(json.dumps(data.response))


class Overpass(object):

    pattern = (
        "[out:{format}][timeout:{timeout}]{maxsize};"
        "({query_type}{filters}{within};>;);"
        "out {meta};"
    )

    url = "http://www.overpass-api.de/api/interpreter"

    cache = OSMCache()

    cache_expiration = pd.Timedelta("3650 days")  # infinity?

    def get_query(self, format_: str, **kwargs) -> str:

        if "maxsize" not in kwargs:
            kwargs["maxsize"] = ""

        if "timeout" not in kwargs:
            kwargs["timeout"] = 180

        kwargs["format"] = format_
        query_str = self.pattern.format(**kwargs)

        return query_str

    def json_request(
        self,
        query_type: str,
        where: Optional[LocationType] = None,
        requests_extra: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Response:
        if requests_extra is None:
            requests_extra = dict()

        if isinstance(where, str):
            where = location(where)
        if isinstance(where, int):  # osm_id
            within = "({})".format(where)
        elif isinstance(where, Nominatim):
            pattern = "({south:.8f},{west:.8f},{north:.8f},{east:.8f})"
            within = pattern.format(**where.bbox._asdict())
        elif isinstance(where, Iterable):
            pattern = "({:.8f},{:.8f},{:.8f},{:.8f})"
            west, south, east, north = where  # bounds order seems more natural
            within = pattern.format(south, west, north, east)
        else:
            within = ""

        filters = ""
        for key, value in kwargs.items():
            if value is None:
                filters += '["{}"]'.format(key)
            else:
                filters += '["{}"~"{}"]'.format(key, value)

        query_str = self.get_query(
            "json",
            meta="",
            query_type=query_type,
            filters=filters,
            within=within,
        )

        return self.query(query_str)

    def query(
        self, query_str: str, requests_extra: Optional[Dict[str, str]] = None
    ) -> Response:

        from .. import session

        if requests_extra is None:
            requests_extra = dict()

        hashcode = hashlib.md5(query_str.encode("utf-8")).hexdigest()
        response = self.cache.get(hashcode, None)
        if response is not None:
            last_modification = pd.Timestamp(
                response.response["osm3s"]["timestamp_osm_base"]
            )
            delta = pd.Timestamp("now", tz="utc") - last_modification
            if delta <= self.cache_expiration:
                logging.info(f"Footprint loaded from cache: {last_modification}")
                return response
            logging.warning(
                "Expired cache files. Downloading now from OpenStreetMap."
            )

        try:
            response = session.post(
                url=self.url, data=query_str, **requests_extra
            )
            response = Response(response.json(), hashcode)
            self.cache[hashcode] = response
            return response
        except requests.ConnectionError:
            # in case connection is down but you still have an old cache
            # you may want to keep it for now
            if response is not None:
                return response
            raise

    # more natural than a subsequent call to json_request!
    def __call__(
        self, where: Optional[LocationType] = None, **kwargs
    ) -> Response:
        return self.json_request(where=where, **kwargs)


request = Overpass()
