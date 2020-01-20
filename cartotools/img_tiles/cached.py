import os

import numpy as np
from concurrent import futures
from PIL import Image

from cartopy.io.img_tiles import _merge_tiles
from appdirs import user_cache_dir

global_cache_dir = user_cache_dir("cartotools")
if not os.path.isdir(global_cache_dir):
    os.makedirs(global_cache_dir)


class Cache(object):

    extension = ".jpg"

    def __init__(self, *args, **kwargs):
        super(Cache, self).__init__(*args, **kwargs)
        self.params = {}

        tileset_name = "{}".format(self.__class__.__name__.lower())
        self.cache_directory = os.path.join(global_cache_dir, tileset_name)

    @property
    def cache_directory(self):
        return self.cache_dir

    @cache_directory.setter
    def cache_directory(self, global_cache_dir):
        global_cache_dir = os.path.expanduser(global_cache_dir)

        tileset_name = "{}".format(self.__class__.__name__.lower())
        self.cache_dir = os.path.join(global_cache_dir, tileset_name)
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def get_image(self, tile):
        from .. import session

        tile_fname = os.path.join(
            self.cache_dir, "_".join(str(v) for v in tile) + self.extension
        )

        if not os.path.exists(tile_fname):
            response = session.get(
                self._image_url(tile), stream=True, **self.params
            )

            with open(tile_fname, "wb") as fh:
                for chunk in response:
                    fh.write(chunk)

        with open(tile_fname, "rb") as fh:
            img = Image.open(fh)
            img = img.convert(self.desired_tile_form)

        return img, self.tileextent(tile), "lower"

    def one_image(self, tile):
        img, extent, origin = self.get_image(tile)
        img = np.array(img)
        x = np.linspace(extent[0], extent[1], img.shape[1])
        y = np.linspace(extent[2], extent[3], img.shape[0])
        return [img, x, y, origin]

    def image_for_domain(self, target_domain, target_z):
        tiles = []
        with futures.ThreadPoolExecutor(max_workers=20) as executor:
            todo = {}
            for tile in self.find_images(target_domain, target_z):
                future = executor.submit(self.one_image, tile)
                todo[future] = tile

            done_iter = futures.as_completed(todo)
            for future in done_iter:
                try:
                    res = future.result()
                except IOError:
                    continue
                tiles.append(res)
        img, extent, origin = _merge_tiles(tiles)
        return img, extent, origin
