from .tags_extra import *

airport = {"query_type": 'way["aeroway"]'}

# -- Amenities --

fountain = {"query_type": "way", "amenity": "fountain"}
marketplace = {"query_type": "way", "amenity": "marketplace"}
place_of_worship = {"query_type": "way", "amenity": "place_of_worship"}
recycling = {"query_type": "way", "amenity": "recycling"}
waste_disposal = {"query_type": "way", "amenity": "waste_disposal"}

# -- Leisure  --

park = {"query_type": "way", "leisure": "park"}
stadium = {"query_type": "way", "leisure": "stadium"}
swimming_pool = {"query_type": "way", "leisure": "swimming_pool"}

# -- Power --

biomass = {"query_type": 'node["power"]', "generator:source": "biomass"}
coal_power = {"query_type": 'node["power"]', "generator:source": "coal_power"}
gas_plant = {"query_type": 'node["power"]', "generator:source": "gas"}
hydroelectric = {"query_type": 'node["power"]', "generator:source": "hydro"}
nuclear_plant = {"query_type": 'node["power"]', "generator:source": "nuclear"}
oil_plant = {"query_type": 'node["power"]', "generator:source": "oil"}
solar_power = {"query_type": 'node["power"]', "generator:source": "solar"}
wave_power = {"query_type": 'node["power"]', "generator:source": "wave"}
wind_turbine = {"query_type": 'node["power"]', "generator:source": "wind"}

waste_incineration = {
    "query_type": 'node["power"]',
    "generator:source": "waste",
}

pipeline = {"query_type": "way", "man_made": "pipeline"}

# -- Sport --

golf = {"query_type": "ways", "sport": "golf"}
horse_racing = {"query_type": "ways", "sport": "horse_racing"}
skatepark = {"query_type": "ways", "sport": "skatepark"}
tennis = {"query_type": "ways", "sport": "tennis"}
tree = {"query_type": "nodes", "natural": "tree"}

# -- Waterway --

river = {"query_type": "way", "waterway": "river"}
riverbank = {"query_type": "way", "waterway": "riverbank"}
stream = {"query_type": "way", "waterway": "stream"}
canal = {"query_type": "way", "waterway": "canal"}
