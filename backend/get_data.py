# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""
# Standard library
import requests
# Third party

# Local imports


def request_access_token(client_id: str,
                         client_secret: str,
                         refresh_token: str) -> str:
    """
    Send a post request to the Strava API to get an access token. In case the response
    is not ok an empty string is return.

    Parameters
    ----------
    client_id : str
        The Strava Client ID.
    client_secret : str
        The Strava Secret code.
    refresh_token : str
        The Strava Refresh token.

    Returns
    -------
    token: str
        The token from the response or an empty string.

    """
    token : str = ""

    auth_url : str = "https://www.strava.com/oauth/token"
    payload : dict = {"client_id": client_id,
                      "client_secret": client_secret,
                      "refresh_token": refresh_token,
                      "grant_type": "refresh_token",
                      "f": "json"}

    response = requests.post(auth_url,
                             data=payload,
                             verify=False)
    if response.ok:
        token = response.json()['access_token']
        return token
    return token


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
        print(request_page_num, response.status_code, type(data_set))
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
