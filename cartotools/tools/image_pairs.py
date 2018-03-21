from collections import Iterable
from functools import partial
from pathlib import Path
from typing import Iterator, Tuple, Optional

import numpy as np
from matplotlib.path import Path as Mpl_Path

import pyproj
from cartotools import img_tiles
from cartotools.osm import location, request, tags
from shapely.ops import transform


def image_pairs(name: str, tag: str, zoom_level: int = 13,
                cache_dir: Optional[Path] = None,
                service: str = 'ArcGIS'
                ) -> Iterator[Tuple[np.ndarray, np.ndarray]]:

    response = request.json_request(location[name], **getattr(tags, tag))
    response.geometry()

    ag = getattr(img_tiles, service)()
    if cache_dir is not None:
        ag.cache_directory = cache_dir.as_posix()

    partial_t = partial(
        pyproj.transform,
        pyproj.Proj(init='EPSG:4326'),
        pyproj.Proj(**ag.crs.proj4_params))

    target = transform(partial_t, response.geometry())

    for coords in ag.find_images(target, zoom_level):
        x = ag.one_image(coords)
        X, Y = np.meshgrid(x[1], x[2])

        output = np.zeros_like(X, np.bool)
        points = np.hstack((X.flatten()[:, np.newaxis],
                            Y.flatten()[:, np.newaxis]))

        if not isinstance(target, Iterable):
            target = [target]

        for g in target:
            flags = Mpl_Path(np.stack(g.buffer(5).exterior.coords)
                             ).contains_points(points)
            output |= flags.reshape(X.shape).astype(np.bool)

        yield x[0], output
