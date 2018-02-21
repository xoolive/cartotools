
import random

from . import GoogleTiles
from .cached import Cache

microsoftToCorners = {'00': '0', '01': '1', '10': '2', '11': '3'}
octalStrings = ('000', '001', '010', '011', '100', '101', '110', '111')

def toBinaryString(i):
    """ Return a binary string for an integer.
    """
    return ''.join([octalStrings[int(c)]
                    for c in oct(i)[2:]]).lstrip('0')

def toMicrosoft(x, y, zoom):
    """ Return string for Microsoft tile column, row, zoom.
    """
    y, x = toBinaryString(y).rjust(zoom, '0'), toBinaryString(x).rjust(zoom, '0')
    return ''.join([microsoftToCorners[y[c]+x[c]] for c in range(zoom)])

class Bing(Cache, GoogleTiles):
    """
    """
    def _image_url(self, tile):
        x, y, z = tile
        return 'http://a%d.ortho.tiles.virtualearth.net/tiles/a%s.jpeg?g=90' % (random.randint(0, 3), toMicrosoft(x, y, z))
