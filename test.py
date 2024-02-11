# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""

import json
import geopy.geocoders
import plotly.express as px
import tqdm
import backend.strava_parser as bsp
import backend.utils as bu

tqdm.tqdm.pandas()
path = "C:/Users/joost/Python/activity_mapper_v2/strava.txt"

with open(path, mode="r") as file:
    df = bsp.parse([json.loads(l)
                    for l in file.readlines()]
                   )


geolocator = geopy.geocoders.Nominatim(user_agent="appje")
locs = df.loc[~df.lat.isna()]

def locate_country(row):
    coords = ", ".join(map(str,[row.lat, row.lon]))
    location = geolocator.reverse(coords)
    country = location.raw.get("address").get("country")
    return country

locs["country"] = locs.progress_apply(locate_country, axis="columns")
print(locs.country.value_counts())
