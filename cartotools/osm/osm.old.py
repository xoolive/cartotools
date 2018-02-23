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


def get_roads_json(south, north, west, east):

    filters_road = ('["area"!~"yes"]["highway"~"motorway|primary"]')
    query_str = query.format(north=north, south=south, east=east, west=west,
                             infrastructure='way["highway"]',
                             filters=filters_road,
                             timeout=180, maxsize='')

    response_json = overpass_request(data={'data': query_str}, timeout=180)

    return response_json
