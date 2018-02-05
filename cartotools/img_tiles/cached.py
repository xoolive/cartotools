import os
import time
import hashlib
import requests

import numpy as np
from concurrent import futures
from PIL import Image

from cartopy.io.img_tiles import _merge_tiles
from appdirs import user_cache_dir

global_cache_dir = user_cache_dir("cartotools")
if not os.path.isdir(global_cache_dir):
    os.makedirs(global_cache_dir)


class Cache(object):

    extension = '.jpg'
    md5_unavailable = None

    def __init__(self, *args, **kwargs):
        super(Cache, self).__init__(*args, **kwargs)
        self.params = {}

        tileset_name = '{}'.format(self.__class__.__name__.lower())
        self.cache_directory = global_cache_dir
        self.progressbar = None

    def notebook(self):
        import tqdm
        self.progressbar = tqdm.tqdm_notebook

    def progressbar(self):
        import tqdm
        self.progressbar = tqdm.tqdm

    @property
    def cache_directory(self):
        return self.cache_dir

    @cache_directory.setter
    def cache_directory(self, global_cache_dir):
        global_cache_dir = os.path.expanduser(global_cache_dir)

        tileset_name = '{}'.format(self.__class__.__name__.lower())
        self.cache_dir = os.path.join(global_cache_dir, tileset_name)
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def get_image(self, tile):
        x, y, z = tuple(str(v) for v in tile)
        tile_dir = os.path.join(self.cache_dir, z, y)
        tile_fname = os.path.join(tile_dir, '{}_{}_{}'.format(x, y, z) +
                                  self.extension)

        if not os.path.exists(tile_fname):
            response = requests.get(self._image_url(tile), stream=True,
                                    **self.params)

            if (self.md5_unavailable is not None and
                    self.md5_unavailable ==
                    hashlib.md5(response.content).hexdigest()):
                return None, self.tileextent(tile), 'lower'

            if not os.path.exists(tile_dir):
                os.makedirs(tile_dir)

            with open(tile_fname, "wb") as fh:
                for chunk in response:
                    fh.write(chunk)

        with open(tile_fname, 'rb') as fh:
            img = Image.open(fh)
            img = img.convert(self.desired_tile_form)

        return img, self.tileextent(tile), 'lower'

    def one_image(self, tile):
        img, extent, origin = self.get_image(tile)
        if img is None:
            return None
        img = np.array(img)
        x = np.linspace(extent[0], extent[1], img.shape[1])
        y = np.linspace(extent[2], extent[3], img.shape[0])
        return [img, x, y, origin]

    def image_for_domain(self, target_domain, target_z):
        tiles = []
        failed = []
        with futures.ThreadPoolExecutor(max_workers=20) as executor:
            todo = {}
            for tile in self.find_images(target_domain, target_z):
                future = executor.submit(self.one_image, tile)
                todo[future] = tile

            done_iter = futures.as_completed(todo)
            if self.progressbar is not None:
                done_iter = self.progressbar(done_iter, total=len(todo))

            for future in done_iter:
                try:
                    res = future.result()
                except IOError:
                    # Try once more...
                    tile = todo[future]
                    # We will try again
                    failed.append(tile)
                    continue

                if res is not None:
                    tiles.append(res)

        # For tiles which failed in parallel (just in case)
        if len(failed) > 0:
            print("Wait for a bit...")
            time.sleep(3)

            if self.progressbar is not None:
                failed = self.progressbar(failed)

            for tile in failed:
                try:
                    res = self.one_image(tile)
                except IOError as e:
                    print(f"IOError for tile: {tile}")
                    print(e)

                if res is not None:
                    tiles.append(res)

        img, extent, origin = _merge_tiles(tiles)
        return img, extent, origin
