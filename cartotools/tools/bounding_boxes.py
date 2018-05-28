from functools import partial
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

import numpy as np

import pyproj
from cartotools import img_tiles
from cartotools.osm import request, tags
from cartotools.osm.nominatim import LocationType
from shapely.geometry import base, box
from shapely.ops import cascaded_union, transform


def compute_coords(img_tuple, bounds):
    return (sum(bounds[0] >= img_tuple[0]),
            sum(bounds[3] <= img_tuple[1]),  # reversed because y goes upwards
            sum(bounds[2] >= img_tuple[0]),
            sum(bounds[1] <= img_tuple[1]))


def make_pair(coords: Tuple[int, int, int], ag,
              target: Dict[int, base.BaseGeometry],
              buffer: Dict[int, Optional[int]]=None
              ) -> Tuple[np.ndarray, Tuple[np.ndarray, np.ndarray]]:

    x = ag.one_image(coords)
    return x[0], (x[1], x[2])


def rec_make_pair(coords: Tuple[int, int, int], augment: int,
                  ag, target: Dict[int, base.BaseGeometry],
                  buffer: Dict[int, Optional[int]]
                  ) -> Tuple[np.ndarray, Tuple[np.ndarray, np.ndarray]]:

    if augment == 0:
        return make_pair(coords, ag, target, buffer)
    else:
        x, y, z = coords

        x0, next0 = rec_make_pair((2*x, 2*y, z+1),
                                  augment-1, ag, target, buffer)
        x1, next1 = rec_make_pair((2*x+1, 2*y, z+1),
                                  augment-1, ag, target, buffer)
        x2, next2 = rec_make_pair((2*x, 2*y+1, z+1),
                                  augment-1, ag, target, buffer)
        x3, next3 = rec_make_pair((2*x+1, 2*y+1, z+1),
                                  augment-1, ag, target, buffer)

        img = np.vstack([np.hstack([x0, x1]), np.hstack([x2, x3])])
        next_ = (np.hstack([next0[0], next3[0][1:]]),
                 np.hstack([next3[1], next0[1][1:]]))

        return img, next_


def yield_bbox(coords: Tuple[int, int, int], augment: int,
               ag, target: Dict[int, base.BaseGeometry],
               buffer: Dict[int, Optional[int]]
               )-> Tuple[np.ndarray,
                         List[Tuple[int, Tuple[float, float, float, float]]]]:

    img, next_ = rec_make_pair(coords, augment, ag, target, buffer)
    bbox = box(next_[0][0], next_[1][0], next_[0][-1], next_[1][-1])

    output = []
    for idx, geometry in target.items():
        for g in geometry:
            if buffer[idx] is not None:
                g = g.buffer(buffer[idx])
            if bbox.intersects(g):
                output.append((idx, compute_coords(next_, g.bounds)))

    return img, output


def bounding_box(name: LocationType, tag: Dict[int, str],
                 zoom_level: int = 13, augment: int = 0,
                 cache_dir: Optional[Path] = None,
                 service: str='ArcGIS',
                 ) -> Iterator[Tuple[np.ndarray, List]]:

    response = {k: request(name, **getattr(tags, t))
                for k, t in tag.items()}

    buffer = {k: tags.node_width.get(v, None) for k, v in tag.items()}

    ag = getattr(img_tiles, service)()
    if cache_dir is not None:
        ag.cache_directory = cache_dir.as_posix()

    partial_t = partial(
        pyproj.transform,
        pyproj.Proj(init='EPSG:4326'),
        pyproj.Proj(**ag.crs.proj4_params))

    target = {k: transform(partial_t, r.shape) for k, r in response.items()}

    for coords in ag.find_images(cascaded_union(target.values()), zoom_level):
        yield coords, yield_bbox(coords, augment, ag, target, buffer)
