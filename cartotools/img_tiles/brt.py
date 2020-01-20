from . import GoogleTiles
from .cached import Cache

"""
Nationaal Georegister

http://www.nationaalgeoregister.nl/geonetwork/srv/dut/catalog.search#/map

"""


class BRT_Achtergrond(Cache, GoogleTiles):
    """
    De achtergrondkaart PDOK is de kaartlaag waarop locatiegebonden
    content wordt afgebeeld. De achtergrondkaart moet ervoor zorgen
    dat de eindgebruiker zich kan orienteren tijdens het gebruik
    van geografische applicaties. Data automatisch gegeneraliseerd
    op basis van TOP10NL. Buiten de standaard projectie EPSG:28992
    (Amersfoort / RD New) wordt deze service ook geleverd in de
    projectie EPSG:25831 (ETRS89 / UTM zone 31N).

    Basisregistratie Topografie

    """

    layer = "brtachtergrondkaart"
    extension = ".png"

    def _image_url(self, tile):
        x, y, z = tile
        url = (
            "http://geodata.nationaalgeoregister.nl/wmts/?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=%s&STYLE=default&TILEMATRIXSET=EPSG:3857&TILEMATRIX=EPSG:3857:%s&TILEROW=%s&TILECOL=%s&FORMAT=image/png8"
            % (self.layer, z, y, x)
        )
        return url
