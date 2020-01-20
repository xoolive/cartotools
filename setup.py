from setuptools import setup

setup(
    name="cartotools",
    version="1.2",
    description="Making cartopy suit my needs",
    license="MIT",
    packages=[
        "cartotools",
        "cartotools.crs",
        "cartotools.img_tiles",
        "cartotools.osm",
    ],
    author="Xavier Olive",
)
