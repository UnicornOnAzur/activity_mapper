# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""

# Standard library
import os
import requests
import typing
# Third party
import pandas as pd
import polyline
# Local imports
import backend.utils as bu

AUTH_LINK = "https://www.strava.com/oauth/token"
STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")

def get_access_token(authorization_code):
    """


    Parameters
    ----------
    authorization_code : TYPE
        DESCRIPTION.

    Returns
    -------
    athlete_name : TYPE
        DESCRIPTION.
    access_token : TYPE
        DESCRIPTION.
    refresh_token : TYPE
        DESCRIPTION.

    """
    res = bu.post_request(AUTH_LINK,
                          data={"client_id":STRAVA_CLIENT_ID,
                                "client_secret": STRAVA_CLIENT_SECRET,
                                "code": authorization_code,
                                "grant_type": "authorization_code"})
    athlete_name = " ".join((res.get("athlete", {}).get("firstname", ""),
                             res.get("athlete", {}).get("lastname", "")
                             )
                            )
    refresh_token = res.get("refresh_token")
    access_token = res.get("access_token")
    return athlete_name, access_token, refresh_token


def request_data_from_api(access_token: str) -> list[dict]:
    """
    Send get requests in a loop to retreive all the activities. Loop will stop if
    the result is empty implying that all activities have been retrieved.

    Parameters
    ----------
    access_token : str
        DESCRIPTION.

    Returns
    -------
    list[dict]
        DESCRIPTION.

    """
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    header = {"Authorization": f"Bearer {access_token}"}
    request_page_num = 1
    all_activities = []

    while True:
        param = {"per_page": 200,
                 "page": request_page_num}
        response = requests.get(activities_url,
                                headers=header,
                                params=param)
        data_set = response.json()
        # print(request_page_num, response.status_code, type(data_set))
        if not response.ok:
            all_activities.append(data_set)
            return all_activities
        # break out of the loop if the response is empty
        if len(data_set) == 0:
            break
        # add onto the list
        if all_activities:
            all_activities.extend(data_set)
        # populate the list if it is empty
        else:
            all_activities = data_set
        # increment to get the next page
        request_page_num += 1
    return all_activities


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
        elements = {"view on Strava": f"https://www.strava.com/activities/{activity.get('id')}",
                    "name": activity.get("name"),
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
