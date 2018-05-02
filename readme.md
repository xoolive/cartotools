## Making cartopy suit my needs

`cartotools` include new projections, caches image tiles from WMTS services, and provides image tiles from various national SIG providers (Pseudo-Mercator only, *maybe* "for now").

### Installation

```bash
sudo apt-get install libproj-dev
pip install Cartopy
pip install requests pillow OSWLib appdirs
python setup.py install
```

### Usage

For now, just replace:

```python
import cartotools.crs  # instead of cartopy.crs
import cartotools.img_tiles  # instead of cartopy.io.img_tiles
```

### Openstreetmap

```python
from cartotools.osm import location, request, tags
```

### Scripts

Get all tiles (zoom level 13) in geolocation "Occitanie" matching tag "wind_turbine" in Openstreetmap.

```sh
python scripts/get_tiles.py -b Occitanie -g wind_turbine  -z 13 -o cache
```

### More code

See https://gitlab.com/xoolive/cartotools/snippets
