# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

All the functions and variables related to using the Strava API and it's data.
"""

# Standard library
import typing
# Third party
import pandas as pd
import polyline
import streamlit as st
# Local imports
import backend

COUNTRIES = backend.load_country_code_mapper(backend.PATH_CODES)


def get_access_token(authorization_code: str) -> tuple[str]:
    """
    <>

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
    res = backend.post_request(backend.TOKEN_LINK,
                               data={"client_id": backend.STRAVA_CLIENT_ID,
                                     "client_secret": backend.STRAVA_CLIENT_SECRET,
                                     "code": authorization_code,
                                     "grant_type": "authorization_code"})
    access_token = res.get("access_token")
    refresh_token = res.get("refresh_token")
    athlete_name = " ".join((res.get("athlete", {}).get("firstname", ""),
                             res.get("athlete", {}).get("lastname", "")
                             )
                            )
    created_at = res.get("athlete", {}).get("created_at", "Not found")
    return access_token, refresh_token, athlete_name, created_at


def refresh_access_token(refresh_token):
    response = backend.post_request(backend.TOKEN_LINK,
                                    data={"client_id": backend.STRAVA_CLIENT_ID,
                                          "client_secret": backend.STRAVA_CLIENT_SECRET,
                                          "grant_type": "refresh_token",
                                          "refresh_token": refresh_token}
                                    )
    refresh_token = response.get("refresh_token")
    access_token = response.get("access_token")
    athlete = backend.get_request("https://www.strava.com/api/v3/athlete",
                                  headers = {"Authorization": f"Bearer {access_token}"})
    athlete_name = " ".join((athlete.get("firstname", ""),
                             athlete.get("lastname", "")
                             )
                            )
    created_at = athlete.get("created_at", "Not found")
    return access_token, refresh_token, athlete_name, created_at


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
    header = {"Authorization": f"Bearer {access_token}"}
    request_page_num = 1
    all_activities = []

    while True:
        param = {"per_page": 200,
                 "page": request_page_num}
        response = backend.get_request(url=backend.ACTIVITIES_LINK,
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
        if len(response) < 200:
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


@st.cache_data()
def nomatim_lookup(lat, lon):
    # print(f"api_call with {lat=}, {lon=}")
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
        elements = {"id": activity.get("id"),
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
                             "country": locate_country(*tuple(map(lambda x: (s:=str(round(x, 1))).ljust(len(s.split(".")[0])+2, "0"),
                                                                  [elements.get("lat"),
                                                                   elements.get("lon")]
                                                                  )
                                                              )
                                                       )
                             }
                            )
        parsed_activities.append(elements)
    # <>
    dataframe = pd.DataFrame(parsed_activities)
    dataframe["app"] = "Strava"
    return dataframe


if __name__ == "__main__":
    pass