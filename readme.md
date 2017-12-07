## Making cartopy suit my needs

`cartotools` include new projections, caches image tiles from WMTS services, and provides image tiles from various national SIG providers (Pseudo-Mercator only, *maybe* "for now").

### Installation

```bash
# in addition to cartopy
pip install requests pillow oswlib appdirs
pip install git+https://github.com/xoolive/cartotools
```

### Usage

For now, just replace:

```python
import cartotools.crs  # instead of cartopy.crs
import cartotools.img_tiles  # instead of cartopy.io.img_tiles
```
