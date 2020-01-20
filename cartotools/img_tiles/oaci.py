from . import GoogleTiles
from .cached import Cache


class DFS_OACI(Cache, GoogleTiles):
    def _image_url(self, tile):
        x, y, z = tile
        return (
            "https://secais.dfs.de/static-maps/ICAO500-2015-EUR-Reprojected_07/tiles/%s/%s/%s.png"
            % (z, x, y)
        )


class AIP_Drones(Cache, GoogleTiles):
    def _image_url(self, tile):
        x, y, z = tile
        return "http://www.aip-drones.fr/carte/tiles/oaci/%s/%s/%s.png" % (
            z,
            x,
            y,
        )
