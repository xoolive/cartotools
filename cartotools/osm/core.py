import requests

def json_request(url, timeout=180, **kwargs):
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

    response = requests.post(url, timeout=timeout, **kwargs)

    try:
        response_json = response.json()
    except Exception:
        # 429 is 'too many requests' and 504 is 'gateway timeout' from server
        # overload - handle these errors by recursively calling
        # overpass_request until we get a valid response
        if response.status_code in [429, 504]:
            # pause for error_pause_duration seconds before re-trying request
            time.sleep(1)
            response_json = json_request(url, timeout=timeout, **kwargs)

        # else, this was an unhandled status_code, throw an exception
        else:
            raise Exception('Server returned no JSON data.\n{} {}\n{}'.format(
                response, response.reason, response.text))

    return response_json

