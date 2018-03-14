# geodata.py --type [osm, generator:source] --boundingbox "occitanie"
# --sat-source "arcgis"

from cartotools import img_tiles
from cartotools.crs import PlateCarree
from cartotools.osm import get, request, tags
from shapely.geometry import MultiPoint
from tqdm import tqdm


# xml = request.xml_request(get['France'], **windmills)
# import tempfile#
#
# _, name = tempfile.mkstemp(text=True, suffix='.osm')
# with open(name, 'w', encoding='utf8') as fh:
#    fh.write(xml)

# from shapely.ops import cascaded_union

# db = records.Database('postgres://xolive:osm_@localhost/europe')
# rows = db.query('select osm_id,"generator:source",ST_AsGeoJSON(way)
# as geojson from planet_osm_point where "generator:source"=\'wind\';')
# geojson = rows.export('df')['geojson']
# domain = cascaded_union([shape(json.loads(g)) for g in geojson])
# domain
# nodes/ways


def get_data(location: str, category: str, zoom_level: int,
             cache_directory: str, sat_source: str):
    json = request.json_request(get[location], **getattr(tags, category))
    domain = MultiPoint([(x['lon'], x['lat']) for x in json.nodes.values()])

    tile_server = getattr(img_tiles, sat_source)()
    tile_server.cache_directory = cache_directory

    target = tile_server.crs.project_geometry(domain, PlateCarree())
    list_tiles = list(tile_server.find_images(target.buffer(50), zoom_level))

    for tile in tqdm(list_tiles):
        tile_server.one_image(tile)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Get tiles associated to a specific category")

    parser.add_argument("category",
                        help="name of the OSM category to search for")

    parser.add_argument("location", default="Toulouse",
                        help="name of the area to search for")

    parser.add_argument("-z", dest="zoom_level", default=10, type=int,
                        help="zoom level (up to 19)")

    parser.add_argument("-c", dest="cache_directory", default="cache",
                        help="cache directory for tiles")

    parser.add_argument("-s", dest="sat_source", default="ArcGIS",
                        help="Source for satellite images")

    get_data(**vars(parser.parse_args()))
