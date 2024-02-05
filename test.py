# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""

import json
import backend.strava_parser as bsp

path = "C:/Users/joost/Python/activity_mapper_v2/strava.txt"

with open(path, mode="r") as file:
    df = bsp.parse([json.loads(l)
                    for l in file.readlines()]
                   )
