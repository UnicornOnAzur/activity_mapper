# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""

# Standard library
# import concurrent
# import functools
import os
import typing
# Third party
import pandas as pd
import polyline
import streamlit as st
# Local imports
import backend

STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")
COUNTRIES = backend.load_country_code_mapper(backend.PATH_CODES)

def get_access_token(authorization_code: str) -> tuple[str]:
    """


    Parameters
    ----------
    authorization_code : str
        DESCRIPTION.

    Returns
    -------
    athlete_name : str
        DESCRIPTION.
    access_token : str
        DESCRIPTION.
    refresh_token : str
        DESCRIPTION.
    created_at : str
        DESCRIPTION.
    """
    res = backend.post_request(backend.AUTH_LINK,
                          data={"client_id": STRAVA_CLIENT_ID,
                                "client_secret": STRAVA_CLIENT_SECRET,
                                "code": authorization_code,
                                "grant_type": "authorization_code"})
    athlete_name = " ".join((res.get("athlete", {}).get("firstname", ""),
                             res.get("athlete", {}).get("lastname", "")
                             )
                            )
    refresh_token = res.get("refresh_token")
    access_token = res.get("access_token")
    created_at = res.get("athlete", {}).get("created_at", "Not found")
    return athlete_name, access_token, refresh_token, created_at


def request_data_from_api(access_token: str) -> list[dict]:
    """
    Send get requests in a loop to retreive all the activities. Loop will stop
    if the result is empty implying that all activities have been retrieved.

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
        response = backend.get_request(url=activities_url,
                                  headers=header,
                                  params=param)
        # if an invalid response is received
        # return the message and stop looping
        if isinstance(response, dict):
            all_activities.append(response)
            break
        # otherwise add the response to the list
        all_activities.extend(response)
        # if the page is empty or less than 200 records stop the loop
        if len(response) < 200 or response == []:
            break
        # increment to get the next page
        request_page_num += 1
    return all_activities


def get_lat_long(value: list[float]) -> list[typing.Union[None, float]]:
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


def get_country(row):
    print(pd.isna(row.get("lat")), f"{row.get('lat')=}", f"{row.get('lon')=}")
    if pd.isna(row.get("lat")):
        return None
    located_country = locate_country(*tuple(map(lambda x:(s:=str(round(x,3))).ljust(len(s.split(".")[0])+4, "0"),
                                                [row.get("lat"),
                                                 row.get("lon")]
                                                )
                                            )
                                     )
    return located_country


@st.cache_data
def nomatim_lookup(lat, lon):
    print(f"api_call with {lat=}, {lon=}")
    response: dict = backend.get_request(backend.NOMINATIM_LINK,
                                    params={"lat": lat,
                                            "lon": lon,
                                            "format": "json"})
    return response


def locate_country(lat, lon, mapper=COUNTRIES):
    response = nomatim_lookup(lat, lon)
    country_code: str = response.get("address", {}).get("country_code", "")
    country: str = COUNTRIES.get(country_code.upper(),
                                     "undefined")
    return country


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
    # <>
    for activity in activities:
        timestamp = pd.to_datetime(activity.get("start_date_local"))
        elements = {"view on Strava":
                    f"https://www.strava.com/activities/{activity.get('id')}",
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
                    "polyline": activity.get("map", {}
                                             ).get("summary_polyline")
                    }
        elements.update(dict(zip(["lat", "lon"],
                                 get_lat_long(activity.get("start_latlng",
                                                           [])))))
        if elements.get("polyline"):
            elements.update({"coords": polyline.decode(elements.get("polyline"
                                                                    ),
                                                       5),
                             }
                            )
        parsed_activities.append(elements)
    # <>
    dataframe = pd.DataFrame(parsed_activities)
    dataframe["app"] = "Strava"
    dataframe.sort_values(by=["lat","lon"],
                          inplace=True)
    return dataframe


def parse_coords(dataframe):
    # rows = [row for _, row in dataframe.iterrows()]
    # with concurrent.futures.ThreadPoolExecutor() as threadpool:
    #     countries = list(threadpool.map(get_country, rows, chunksize=1))
    countries = []
    for _, row in dataframe.iterrows():
        countries.append(get_country(row))
    # dataframe["country"] = dataframe.apply(get_country, axis=1)
    dataframe["country"] = countries
    return dataframe


if __name__ == "__main__":
    pass
