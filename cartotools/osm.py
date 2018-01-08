import time
import requests

from collections import OrderedDict

__all__ = ['get_airport_json', 'get_roads_json', 'json_to_shp']

query = ('[out:json][timeout:{timeout}]{maxsize};({infrastructure}{filters}'
         '({south:.8f},{west:.8f},{north:.8f},{east:.8f});>;);out;')


def overpass_request(data, timeout=180):
    """
    Send a request to the Overpass API via HTTP POST and return the JSON
    response.
    Parameters
    ----------
    data : dict or OrderedDict
        key-value pairs of parameters to post to the API
    timeout : int
        the timeout interval for the requests library
    Returns
    -------
    dict

    Reference: https://github.com/gboeing/osmnx/blob/master/osmnx/core.py
    """

    # define the Overpass API URL, then construct a GET-style URL as a string
    # to hash to look up/save to cache

    url = 'http://www.overpass-api.de/api/interpreter'

    response = requests.post(url, data=data, timeout=timeout)

    try:
        response_json = response.json()
    except Exception:
        # 429 is 'too many requests' and 504 is 'gateway timeout' from server
        # overload - handle these errors by recursively calling
        # overpass_request until we get a valid response
        if response.status_code in [429, 504]:
            # pause for error_pause_duration seconds before re-trying request
            time.sleep(1)
            response_json = overpass_request(data=data, timeout=timeout)

        # else, this was an unhandled status_code, throw an exception
        else:
            raise Exception('Server returned no JSON data.\n{} {}\n{}'.format(
                response, response.reason, response.text))

    return response_json


def name_request(query, timeout=30):

    params = OrderedDict()

    params['format'] = 'json'
    params['limit'] = 1
    params['dedupe'] = 0  # this prevents OSM from de-duping results
    # so we're guaranteed to get precisely 'limit' number of results
    params['polygon_geojson'] = 1

    if isinstance(query, str):
        params['q'] = query
    elif isinstance(query, dict):
        # add the query keys in alphabetical order so the URL is the same
        # string each time, for caching purposes
        for key in sorted(list(query.keys())):
            params[key] = query[key]

    url = 'https://nominatim.openstreetmap.org/search'
    response = requests.get(url, params=params, timeout=timeout)
    try:
        response_json = response.json()
    except Exception:
        # 429 is 'too many requests' and 504 is 'gateway timeout' from server
        # overload - handle these errors by recursively calling
        # nominatim_request until we get a valid response
        if response.status_code in [429, 504]:
            time.sleep(1)
            response_json = name_request(params=params, timeout=timeout)

        else:
            raise Exception('Server returned no JSON data.\n{} {}\n{}'.format(
                response, response.reason, response.text))

    return response_json


def get_airport_json(name):

    if isinstance(name, str):
        airport = name_request(name)
        south, north, west, east = tuple(float(f)
                                         for f in airport[0]['boundingbox'])
        south -= .01
        west -= .01
        east += .01
        north += .01
    else:
        assert isinstance(name, tuple)
        west, east, south, north = name

    query_str = query.format(north=north, south=south, east=east, west=west,
                             infrastructure='way["aeroway"]',
                             filters='',
                             timeout=180, maxsize='')

    response_json = overpass_request(data={'data': query_str}, timeout=180)
    response_json['boundingbox'] = list(str(f)
                                        for f in (south, north, west, east))

    return response_json


def json_to_shp(json, shapefile):
    import fiona
    from shapely.geometry import LineString, mapping

    crs = {'no_defs': True, 'ellps': 'WGS84',
           'datum': 'WGS84', 'proj': 'longlat'}
    schema = {'geometry': 'LineString',
              'properties': {'NAME': 'str', 'TYPE': 'str'}}

    nodes = {item['id']: (item['lon'], item['lat'])
             for item in json['elements']
             if item['type'] == 'node'}

    with fiona.open(shapefile, 'w', driver="ESRI Shapefile",
                    crs=crs, schema=schema, encoding='utf-8') as output:

        for item in json['elements']:
            if item['type'] == 'way':
                points = [nodes[int(i)] for i in item['nodes']]
                output.write(
                    {'geometry': mapping(LineString(points)),
                     'properties': {
                         'NAME': item['tags']['name']
                         if 'name' in item['tags'] else '',
                         "TYPE": item['tags']['aeroway']}
                     })


def get_roads_json(south, north, west, east):

    filters_road = ('["area"!~"yes"]["highway"~"motorway|primary"]')
    query_str = query.format(north=north, south=south, east=east, west=west,
                             infrastructure='way["highway"]',
                             filters=filters_road,
                             timeout=180, maxsize='')

    response_json = overpass_request(data={'data': query_str}, timeout=180)

    return response_json
