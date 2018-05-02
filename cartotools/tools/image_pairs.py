from collections import Iterable
from functools import partial
from pathlib import Path
from typing import Dict, Iterator, Tuple, Optional

import numpy as np
from matplotlib.path import Path as Mpl_Path

import pyproj
from cartotools import img_tiles
from cartotools.osm import location, request, tags
from shapely.ops import transform, cascaded_union
from shapely.geometry import base


def make_pair(coords: Tuple[int, int, int], ag,
              target: Dict[int, base.BaseGeometry],
              buffer: Dict[int, Optional[int]]=None) -> Tuple[np.ndarray, np.ndarray]:
    
    x = ag.one_image(coords)
    X, Y = np.meshgrid(x[1], x[2])
    output = np.zeros_like(X, np.uint8)
    mask = np.zeros_like(X, np.bool)
    points = np.hstack((X.flatten()[:, np.newaxis],
                        Y.flatten()[:, np.newaxis]))
    for idx, geometry in target.items():
        for g in geometry:
            if buffer[idx] is not None:
                g = g.buffer(buffer[idx])
            flags = Mpl_Path(np.stack(g.exterior.coords)
                             ).contains_points(points)
            mask |= flags.reshape(X.shape).astype(np.bool) 
        output[mask] = idx
    
    return x[0], output[::-1,:]

def rec_make_pair(coords: Tuple[int, int, int], augment: int,
                  ag, target: Dict[int, base.BaseGeometry],
                  buffer: Dict[int, Optional[int]]) -> Tuple[np.ndarray, np.ndarray]:
    if augment == 0:
        return make_pair(coords, ag, target, buffer)
    else:
        x, y, z = coords

        x0, output0 = rec_make_pair((2*x, 2*y, z+1), augment-1, ag, target, buffer)
        x1, output1 = rec_make_pair((2*x+1, 2*y, z+1), augment-1, ag, target, buffer)
        x2, output2 = rec_make_pair((2*x, 2*y+1, z+1), augment-1, ag, target, buffer)
        x3, output3 = rec_make_pair((2*x+1, 2*y+1, z+1), augment-1, ag, target, buffer)

        return (np.vstack([np.hstack([x0, x1]),
                          np.hstack([x2, x3])]),
               np.vstack([np.hstack([output0, output1]),
                          np.hstack([output2, output3]),]))


def image_pairs(name: str, tag: Dict[int, str],
                zoom_level: int = 13, augment: int = 0,
                cache_dir: Optional[Path] = None,
                service: str='ArcGIS',
               ) -> Iterator[Tuple[np.ndarray, np.ndarray]]:

    response = {k: request.json_request(location[name], **getattr(tags, t))
                for k, t in tag.items()}
    
    buffer = {k: tags.node_width.get(v, None) for k, v in tag.items()}
               
    ag = getattr(img_tiles, service)()
    if cache_dir is not None:
        ag.cache_directory = cache_dir.as_posix()

    partial_t = partial(
        pyproj.transform,
        pyproj.Proj(init='EPSG:4326'),
        pyproj.Proj(**ag.crs.proj4_params))

    target = {k: transform(partial_t, r.geometry()) for k, r in response.items()}

    for coords in ag.find_images(cascaded_union(target.values()), zoom_level):
        yield coords, rec_make_pair(coords, augment, ag, target, buffer)
