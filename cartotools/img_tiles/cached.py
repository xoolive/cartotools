import os
import requests
from PIL import Image

from appdirs import user_cache_dir

global_cache_dir = user_cache_dir("cartotools")
if not os.path.isdir(global_cache_dir):
    os.makedirs(global_cache_dir)

class Cache(object):

    fake_headers = {"Accept": "image/webp,image/*,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, sdch",
                    "Accept-Language": "en-US,en;q=0.8,fr;q=0.6",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
#                     "Host": "wxs.ign.fr",
                    "Pragma": "no-cache",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36"}

    def get_image(self, tile):
        tileset_name = '{}'.format(self.__class__.__name__.lower())
        cache_dir = os.path.join(global_cache_dir, tileset_name)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        tile_fname = os.path.join(cache_dir,
                                  '_'.join(str(v) for v in tile) + '.png')

        if not os.path.exists(tile_fname):
            response = requests.get(self._image_url(tile),
                                    stream=True, headers=self.fake_headers)

            with open(tile_fname, "wb") as fh:
                for chunk in response:
                    fh.write(chunk)

        with open(tile_fname, 'rb') as fh:
            img = Image.open(fh)
            img = img.convert(self.desired_tile_form)

        return img, self.tileextent(tile), 'lower'


