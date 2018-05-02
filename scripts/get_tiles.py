import argparse
from typing import Optional, Tuple, Union

import tqdm
from cartotools import img_tiles, osm
from cartotools.crs import PlateCarree
from concurrent import futures
from shapely.geometry import Polygon

_services = {'arcgis': img_tiles.ArcGIS(),
             'bing': img_tiles.Bing(),
             'osm': img_tiles.OSM()}


type_bbox = Union[Tuple[float, ...], str]


def webcrawl(bbox: type_bbox, cache_directory: Optional[str]=None,
             service: str="arcgis", target_z: int=13,
             max_workers: int=1) -> None:

    webtiles = _services[service]

    if cache_directory is not None:
        webtiles.cache_directory = cache_directory

    if isinstance(bbox, str):
        bbox_str = osm.name_request(bbox)[0]['boundingbox']
        south, north, west, east = tuple(float(f) for f in bbox_str)
        bbox = west, east, south, north

    poly_bbox = Polygon([[bbox[0], bbox[2]], [bbox[0], bbox[3]],
                         [bbox[1], bbox[3]], [bbox[1], bbox[2]]])

    target_domain = webtiles.crs.project_geometry(poly_bbox, PlateCarree())

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
                        help="bounding box for the query")
    parser.add_argument("-t", dest="max_workers", default=1, type=int,
                        help="number of threads for ThreadPoolExecutor")
    parser.add_argument("-o", dest="cache_directory", default="./cache",
                        help="where to store the tiles")
    parser.add_argument("-z", dest="target_z", default=13, type=int,
                        help="zoom level")
    parser.add_argument("-s", dest="service", default="arcgis",
                        help="the source of data")

    args = parser.parse_args()

    webcrawl(**vars(args))
