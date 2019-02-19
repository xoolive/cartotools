## Making cartopy suit my needs

`cartotools` include new projections, caches image tiles from WMTS services, and provides image tiles from various national SIG providers (Pseudo-Mercator only, *maybe* "for now").

### Installation

```bash
sudo apt-get install libproj-dev
pip install Cartopy
pip install requests pillow OWSLib appdirs
pip install git+https://github.com/xoolive/cartotools
```

### Usage

For now, just replace:

```python
import cartotools.crs  # instead of cartopy.crs
import cartotools.img_tiles  # instead of cartopy.io.img_tiles
```
