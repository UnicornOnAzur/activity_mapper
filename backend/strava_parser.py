# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""

# Standard library
import typing
# Third party
import pandas as pd
import polyline
# Local imports


def get_lat_long(value: list[float]) -> list[typing.Union[None,float]]:
    """


    Parameters
    ----------
    value : list[float]
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    if value == []:
        return [None, None]
    return value


def parse(activities: list[dict]) -> pd.DataFrame:
    """


    Parameters
    ----------
    activities : list[dict]
        DESCRIPTION.

    Returns
    -------
    dataframe : TYPE
        DESCRIPTION.

    """
    if activities == [{}]:
        return pd.DataFrame()
    parsed_activities = []
    for activity in activities:
        timestamp = pd.to_datetime(activity.get("start_date_local"),
                                   # format="%Y%m%dT%H:%MZ"
                                   )
        elements = {"name": activity.get("name"),
                    "timestamp": timestamp,
                    "year": timestamp.year,
                    "week": timestamp.week,
                    "calender-week": f"{timestamp.year}-{timestamp.week}",
                    "date": timestamp.date(),
                    "weekday": timestamp.weekday(),
                    "time": timestamp.time(),
                    "hour": timestamp.hour,
                    "minutes": timestamp.minute,
                    "moving_time": activity.get("moving_time"),
                    "type": activity.get("type"),
                    "sport_type": activity.get("sport_type"),
                    "polyline": activity.get("map", {}).get("summary_polyline"),
                    }
        if elements.get("polyline"):
            elements.update({"coords": polyline.decode(elements.get("polyline"), 5)})
        elements.update(dict(zip(["lat","lon"],
                                 get_lat_long(activity.get("start_latlng",
                                                           [])))))
        parsed_activities.append(elements)
    dataframe = pd.DataFrame(parsed_activities)
    dataframe["app"] = "Strava"
    return dataframe


if __name__ == "__main__":
    pass
