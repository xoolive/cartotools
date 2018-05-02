airport = {'infrastructure': 'way["aeroway"]',
           'filters': ''}

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
# - sport=golf,horse_racing,skatepark,tennis
# - tourism=attraction,artwork
# - facilities=dock
# - waterway=waterfall


