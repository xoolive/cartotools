from . import GoogleTiles
from .cached import Cache


"""
Bundesamt für Kartographie und Geodäsie
https://www.bkg.bund.de/DE/Home/home.html


https://www.geodatenzentrum.de/geodaten/gdz_rahmen.gdz_div?gdz_spr=deu&gdz_akt_zeile=2&gdz_anz_zeile=5&gdz_user_id=0
"""


class BKG_Topoplus(Cache, GoogleTiles):
    """
    """

    def _image_url(self, tile):
        x, y, z = tile
        return (
            "http://sgx.geodatenzentrum.de/wmts_topplus_web_open/tile/1.0.0/web/default/WEBMERCATOR/%s/%s/%s.png"
            % (z, y, x)
        )
