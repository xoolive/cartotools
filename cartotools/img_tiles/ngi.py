from . import GoogleTiles
from .cached import Cache

"""
Nationaal Geographisch Instituut
www.ngi.be

Belgium
"""


class NGI_Tiles(GoogleTiles):
    """
    Nationaal Geographisch Instituut
    """

    extension = ".png"

    def _image_url(self, tile):
        x, y, z = tile
        return (
            "http://www.ngi.be/cartoweb/1.0.0/topo/default/3857/%s/%s/%s.png"
            % (z, y, x)
        )
