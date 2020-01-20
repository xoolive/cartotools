# todo


def json_to_shp(json, shapefile):
    import fiona
    from shapely.geometry import LineString, mapping

    crs = {
        "no_defs": True,
        "ellps": "WGS84",
        "datum": "WGS84",
        "proj": "longlat",
    }
    schema = {
        "geometry": "LineString",
        "properties": {"NAME": "str", "TYPE": "str"},
    }

    nodes = {
        item["id"]: (item["lon"], item["lat"])
        for item in json["elements"]
        if item["type"] == "node"
    }

    with fiona.open(
        shapefile,
        "w",
        driver="ESRI Shapefile",
        crs=crs,
        schema=schema,
        encoding="utf-8",
    ) as output:

        for item in json["elements"]:
            if item["type"] == "way":
                points = [nodes[int(i)] for i in item["nodes"]]
                output.write(
                    {
                        "geometry": mapping(LineString(points)),
                        "properties": {
                            "NAME": item["tags"]["name"]
                            if "name" in item["tags"]
                            else "",
                            "TYPE": item["tags"]["aeroway"],
                        },
                    }
                )
