airport = {'infrastructure': 'way["aeroway"]',
           'filters': ''}


river = {'infrastructure': 'way["waterway"]',
           'filters': '["waterway"~"river"]'}

# -- Amenities --

# - amenity=fountain,bench,place_of_worship,marketplace
# - amenity=table,recycling,waste_disposal

place_of_worship = {'infrastructure': 'way["amenity"]',
                    'filters':'["amenity"~"place_of_worship"]'}

marketplace = {'infrastructure': 'way["amenity"]',
               'filters':'["amenity"~"marketplace"]'}

fountain = {'infrastructure': 'way["amenity"]',
            'filters':'["amenity"~"fountain"]'}

waste_disposal = {'infrastructure': 'way["amenity"]',
                  'filters':'["amenity"~"waste_disposal"]'}

recycling = {'infrastructure': 'way["amenity"]',
             'filters':'["amenity"~"recycling"]'}

# -- Leisure  --

park = {'infrastructure': 'way["leisure"]',
         'filters':'["leisure"~"park"]'}  # segmentation

stadium = {'infrastructure': 'way["leisure"]',
           'filters':'["leisure"~"stadium"]'}  # detection

swimming_pool = {'infrastructure': 'way["leisure"]',
                 'filters':'["leisure"~"swimming_pool"]'}  # detection

# -- Power --

# - power=generator,plant,heliostat,bay,busbar,pole,portal,transformer,tower,terminal

wind_turbine = {'infrastructure': 'node["power"]',
                'filters': '["generator:source"~"wind"]'}

nuclear_plant = {'infrastructure': 'node["power"]',
                 'filters': '["generator:source"~"nuclear"]'}

solar_power = {'infrastructure': 'node["power"]',
               'filters': '["generator:source"~"solar"]'}

hydroelectric = {'infrastructure': 'node["power"]',
                 'filters': '["generator:source"~"hydro"]'}

wave_power = {'infrastructure': 'node["power"]',
              'filters': '["generator:source"~"wave"]'}

biomass = {'infrastructure': 'node["power"]',
           'filters': '["generator:source"~"biomass"]'}

coal_power = {'infrastructure': 'node["power"]',
              'filters': '["generator:source"~"biomass"]'}

gas_plant = {'infrastructure': 'node["power"]',
             'filters': '["generator:source"~"gas"]'}

oil_plant = {'infrastructure': 'node["power"]',
             'filters': '["generator:source"~"oil"]'}

waste_incineration  = {'infrastructure': 'node["power"]',
                       'filters': '["generator:source"~"waste"]'}

pipeline = {'infrastructure': 'way["man_made"]',
            'filters': '["man_made"~"pipeline"]'}

# -- Sport --

# - sport=golf,horse_racing,skatepark,tennis

golf = {'infrastructure': 'ways["sport"]',
        'filters': '["sport"~"golf"]'}

horse_racing = {'infrastructure': 'ways["sport"]',
        'filters': '["sport"~"horse_racing"]'}

skatepark = {'infrastructure': 'ways["sport"]',
        'filters': '["sport"~"skatepark"]'}

tennis = {'infrastructure': 'ways["sport"]',
        'filters': '["sport"~"tennis"]'}


tree = {'infrastructure': 'nodes["natural"]',
                  'filters': '["natural"~"tree"]'}

# - barrier=border_control,toll_booth
# - building=bridge (plutot man_made=bridge)
# - building=greenhouse,parking
# - emergency=landing_site
# - public_transport=*
# - highway=street_lamp,traffic_signals
# - man_made=communications_tower,chimney,crane,lighthouse,petroleum_well,silo,storage_tank,water_tower,windmill
# - military=naval_base,barracks,launchpad
# - natural=tree,tree_row
# - natural=volcano,peak
# - place=island,islet,archipelago
# - railway=subway_entrance,tram_stop,turntable,railway_crossing
# - shop=department_store,mall,supermarket,kosk
# - tourism=attraction,artwork
# - facilities=dock
# - waterway=waterfall

# - public_transport=*
# - landuse=*
# - barrier=* -> linear barrier
# - building=*
# - geological=moraine,outcrop
# - highway=* in roads, special roads, paths, ...
# - man_made=pipeline
# - natural=sand
# - natural=water,beach,glacier
# - natural all 'landform'
# - places=* for populated settlements, urban and rural
# - railway=light_rail,monorail,rail,tram
# - tourism=camp_site,caravan_site,zoo,theme_park
# - waterway=river,stream,canal

node_width = {
    'wind_turbine': 27,  # http://energiesduhautlivradois.info/emprise_sol.html
    'pipeline': 5
}