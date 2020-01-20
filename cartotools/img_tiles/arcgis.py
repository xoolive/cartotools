from . import GoogleTiles
from .cached import Cache

"""
ArcGIS satellite images
License: 
http://developer.mapquest.com/web/products/open/map for terms of use
"""


class ArcGIS(Cache, GoogleTiles):
    def _image_url(self, tile):
        x, y, z = tile
        url = (
            "http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/%s/%s/%s"
            % (z, y, x)
        )
        return url
