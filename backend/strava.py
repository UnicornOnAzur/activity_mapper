# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

All the functions and variables related to using the Strava API and it's data.
"""

# Third party
import pandas as pd
import polyline
import streamlit as st
# Local imports
import backend

COUNTRIES = backend.load_country_code_mapper(backend.PATH_CODES)


def get_access(authorization_code: str) -> tuple[str]:
    """
    Given the authorization code in the redirect link get the tokens and the
    details of the athlete who logs in.

    Parameters
    ----------
    authorization_code : str
        The authorization code from the redirect link.

    Returns
    -------
    access_token : str
        The Strava access token.
    refresh_token : str
        The Strava refresh token.
    athlete_name : str
        The combined first and last name of the athlete.
    created_at : str
        The Strava profile creation date.
    """
    response: dict = backend.post_request(backend.TOKEN_LINK,
                                          data={
                                              "client_id":
                                                  backend.STRAVA_CLIENT_ID,
                                              "client_secret":
                                                  backend.STRAVA_CLIENT_SECRET,
                                              "code": authorization_code,
                                              "grant_type":
                                                  "authorization_code"}
                                          )
    access_token: str = response.get("access_token")
    refresh_token: str = response.get("refresh_token")
    # retrieve and combine the first and last name of the athlete
    athlete_name: str = " ".join((response.get("athlete",
                                               {}).get("firstname", ""),
                                  response.get("athlete",
                                               {}).get("lastname", "")
                                  )
                                 )
    created_at: str = response.get("athlete",
                                   {}).get("created_at", "Not found")
    return access_token, refresh_token, athlete_name, created_at


def refresh_access(refresh_token: str) -> tuple[str]:
    """
    Based on the refresh token retrieve the same attributes as the get_access
    function.

    Parameters
    ----------
    refresh_token : str
        The Strava refresh token.

    Returns
    -------
    athlete_name : str
        The combined first and last name of the athlete.
    access_token : str
        The Strava access token.
    refresh_token : str
        The Strava refresh token.
    created_at : str
        The Strava profile creation date.
    """
    response: dict = backend.post_request(backend.TOKEN_LINK,
                                          data={
                                              "client_id":
                                                  backend.STRAVA_CLIENT_ID,
                                              "client_secret":
                                                  backend.STRAVA_CLIENT_SECRET,
                                              "grant_type": "refresh_token",
                                              "refresh_token": refresh_token}
                                          )
    refresh_token: str = response.get("refresh_token")
    access_token: str = response.get("access_token")
    athlete: str = backend.get_request(backend.ATHLETE_URL,
                                       headers={"Authorization":
                                                f"Bearer {access_token}"}
                                       )
    athlete_name: str = " ".join((athlete.get("firstname", ""),
                                  athlete.get("lastname", "")
                                  )
                                 )
    created_at: str = athlete.get("created_at", "Not found")
    return access_token, refresh_token, athlete_name, created_at


@st.cache_data()
def nomatim_lookup(lat: str, lon: str) -> dict:
    """
    Request a reverse location lookup on the Nominatim API.

    Parameters
    ----------
    lat : str
        The latitude.
    lon : str
        The longitude.

    Returns
    -------
    response: dict
        The Nominatim API response containing the country code.

    """
    response: dict = backend.get_request(backend.NOMINATIM_LINK,
                                         params={"lat": lat,
                                                 "lon": lon,
                                                 "format": "json"}
                                         )
    return response


def locate_country(lat: str,
                   lon: str,
                   mapper: dict = COUNTRIES) -> str:
    """
    Locate the country by the coordinates via the reverse lookup with the
    Nominatim API and then map the country code to the country name.

    Parameters
    ----------
    lat : str
        The latitude.
    lon : str
        The longitude.
    mapper : dict, optional
        The mapper of country codes to country names. The default is COUNTRIES.

    Returns
    -------
    country: str
        The country name.

    """
    response: dict = nomatim_lookup(lat, lon)
    country_code: str = response.get("address", {}).get("country_code", "")
    country: str = COUNTRIES.get(country_code.upper(),
                                 "undefined")
    return country


def parse(activities: list[dict]) -> pd.DataFrame:
    """
    Parse the Strava activities for use in the dashboard.

    Decode the polyline to coordinates.
    Reverse lookup the country from start coordinates of the activity.

    Parameters
    ----------
    activities : list[dict]
        List of API responses containing the activities.

    Returns
    -------
    dataframe : pd.DataFrame
        The dataframe containing the parsed activities.

    """
    # if no activities are provided return an empty dataframe.
    if activities == [{}]:
        return pd.DataFrame()
    parsed_activities: list = []
    # for each activity
    for activity in activities:
        # create timestamp from the local start date
        timestamp = pd.to_datetime(activity.get("start_date_local"))
        elements: dict = {"id": activity.get("id"),
                          "name": activity.get("name"),
                          "sport_type": activity.get("sport_type"),
                          "polyline": activity.get("map", {}
                                                   ).get("summary_polyline"),
                          "timestamp": timestamp,
                          "year": timestamp.year,
                          "week": timestamp.week,
                          "calender-week":
                              f"{timestamp.year}-{timestamp.week}",
                          "date": timestamp.date(),
                          "weekday": timestamp.weekday(),
                          "time": timestamp.time(),
                          "hour": timestamp.hour,
                          "minutes": timestamp.minute,
                          }
        # unpack the starting coordinates to lat and lon
        elements.update(dict(zip(
            # keys
            ["lat", "lon"],
            # values
            activity.get("start_latlng",
                         [None, None]
                         )
                                 )
                             )
                        )
        # if there is a polyline for the activity add the individual
        # coordinates to the activity and lookup the country name
        if elements.get("polyline"):
            elements.update({"coords":
                             polyline.decode(
                                 # make a raw string from the polyline
                                 fr"{elements.get('polyline')}",
                                 # precision which is 5 for Google Maps
                                 int=5
                                             ),

                             "country":
                             # provide the function with the coordinates of the
                             # activity as an unpacked tuple of the coordinates
                             # after mapping a rounding to 1 decimal and
                             # filling the strings to the length
                             locate_country(*tuple(map(lambda x:
                                                       # round the string to 1
                                                       # decimal and store it
                                                       (s := str(round(x, 1))
                                                        ).ljust(
                                                        # fill out the string
                                                        # to the length of the
                                                        # rounded string plus 2
                                                        # characters
                                                        len(s.split(".")[0])+2,
                                                        # fill character
                                                        "0"
                                                                ),
                                                       [elements.get("lat"),
                                                        elements.get("lon")]
                                                       )
                                                   )
                                            )
                             }
                            )
        parsed_activities.append(elements)
    # create a dataframe from the dictionary
    dataframe: pd.DataFrame = pd.DataFrame(parsed_activities)
    # add the label Strava to each activity
    dataframe["app"]: pd.Series = "Strava"
    return dataframe


if __name__ == "__main__":
    pass
