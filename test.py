# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""
import time
import json
import backend.strava_parser as bsp
import backend.plotly_charts as bpc

start_time = time.time()
path = "C:/Users/joost/Python/activity_mapper_v2/strava.txt"
with open(path, mode="r") as file:
    df = bsp.parse_coords(bsp.parse([json.loads(l)
                          for l in file.readlines()][-25:]
                         )
               )
locs = df.loc[~df.lat.isna()]
print(locs.country.value_counts())
print(time.time() - start_time)
fig = bpc.locations(locs, 400)
fig.show(renderer="browser")
