from cartopy.io.img_tiles import *

import os.path

from pathlib import Path
from importlib import import_module

for f_py in Path(os.path.dirname(__file__)).glob("[a-z]*.py"):
    mdl = import_module(".{}".format(f_py.with_suffix("").name), __name__)
    if "__all__" in mdl.__dict__:
        # is there an __all__?  if so respect it
        names = mdl.__dict__["__all__"]
    else:
        # otherwise we import all names that don't begin with _
        names = [x for x in mdl.__dict__ if not x.startswith("_")]

    # now drag them in
    globals().update({k: getattr(mdl, k) for k in names})


class GoogleTiles(Cache, GoogleTiles):
    pass


class OSM(Cache, OSM):
    extension = ".png"


class StamenTerrain(Cache, Stamen):
    extension = ".png"

    def __init__(self):
        super().__init__("terrain")
