from . import GoogleTiles
from .cached import Cache

"""
ArcGIS satellite images
License:
http://developer.mapquest.com/web/products/open/map for terms of use
"""

class ArcGIS(Cache, GoogleTiles):

    md5_unavailable = "f27d9de7f80c13501f470595e327aa6d"

    def _image_url(self, tile):
        x, y, z = tile
        url = 'http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/%s/%s/%s' % (z, y, x)
        return url
