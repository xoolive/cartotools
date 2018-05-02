import argparse
from typing import Optional, Tuple, Union
from functools import partial

import tqdm
from cartotools import img_tiles
from cartotools.osm import tags, get, request
from cartotools.crs import PlateCarree
from concurrent import futures
from shapely.geometry import Polygon, Point
from shapely.ops import cascaded_union, transform
import pyproj

_services = {'arcgis': img_tiles.ArcGIS(),
             'bing': img_tiles.Bing(),
             'osm': img_tiles.OSM()}


type_bbox = Union[Tuple[float, ...], str]


def webcrawl(bbox: type_bbox, tag: Optional[str],
             cache_directory: Optional[str]=None,
             service: str="arcgis", target_z: int=13,
             max_workers: int=1) -> None:

    if tag == 'list':
        print(list(t_ for t_ in dir(tags) if "__" not in t_))
        return
    
    webtiles = getattr(img_tiles, service)() #_services[service]

    if cache_directory is not None:
        webtiles.cache_directory = cache_directory

    if tag is None:
        # if no tag, take the whole bounding box
        if isinstance(bbox, str):
            bbox_str = get[bbox]['boundingbox']
            south, north, west, east = tuple(float(f) for f in bbox_str)
            bbox = west, east, south, north
        bbox = Polygon([[bbox[0], bbox[2]], [bbox[0], bbox[3]],
                        [bbox[1], bbox[3]], [bbox[1], bbox[2]]])
    else:
        # otherwise, take only the proper geometries
        response = request.json_request(get[bbox], **getattr(tags, tag))
        bbox = response.geometry()

    target_domain = transform(
        partial(
            pyproj.transform,
            pyproj.Proj(init='EPSG:4326'),
            pyproj.Proj(**webtiles.crs.proj4_params)),
        bbox)
    
    failed = []

    with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        todo = {}
        for tile in webtiles.find_images(target_domain, target_z):
            future = executor.submit(webtiles.one_image, tile)
            todo[future] = tile

        done_iter = futures.as_completed(todo)
        done_iter = tqdm.tqdm(done_iter, total=len(todo))
        for future in done_iter:
            try:
                future.result()
            except IOError:
                failed.append(todo[future])
                continue

    if len(failed) > 0:
        print(f"Catching {len(failed)} failed tiles")
        for tile in tqdm.tqdm(failed):
            webtiles.one_image(tile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Webcrawl for WMTS tiles")

    parser.add_argument("-b", dest="bbox", default="Toulouse",
                        help="bounding box for the query (default: Toulouse)")
    parser.add_argument("-g", dest="tag",
                        help="tag name in OpenStreetMap")
    parser.add_argument("-t", dest="max_workers", default=1, type=int,
                        help="number of threads for ThreadPoolExecutor (default: 1)")
    parser.add_argument("-o", dest="cache_directory", default="/data1/sat",
                        help="where to store the tiles (default: /data1/sat)")
    parser.add_argument("-z", dest="target_z", default=13, type=int,
                        help="zoom level (default: 13)")
    parser.add_argument("-s", dest="service", default="ArcGIS",
                        help="the source of data (default: ArcGIS)")

    args = parser.parse_args()

    webcrawl(**vars(args))
