# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""

# Standard library
import concurrent
import functools
import queue
import threading
import time
import typing
# Third party
import pandas as pd
import polyline
import streamlit as st
# Local imports
import backend

STRAVA_CLIENT_ID = backend.STRAVA_CLIENT_ID
STRAVA_CLIENT_SECRET = backend.STRAVA_CLIENT_SECRET
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
    res = backend.post_request(backend.TOKEN_LINK,
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
        elements = {"view on Strava":
                    f"{backend.ACTIVITIES_URL}{activity.get('id')}",
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
                             "country": locate_country(*tuple(map(lambda x:(s:=str(round(x,1))).ljust(len(s.split(".")[0])+2, "0"),
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


def get_activities_page(queue_in, queue_out, barrier, access_token) -> None:
    # loop forever
    while True:
        # read item from queue
        request_page_num = queue_in.get()
        header = {"Authorization": f"Bearer {access_token}"}
        param = {"per_page": 200, "page": request_page_num}
        response = backend.get_request(url=backend.ACTIVITIES_LINK,
                                       headers=header,
                                       params=param)
        # check for shutdown
        if len(response) <= 200 or isinstance(response, dict):# or request_page_num is None:
            # put signal back on queue
            queue_in.put(None)
        	# wait on the barrier for all other workers
            barrier.wait()
            # send signal on output queue
            queue_out.put(None)
            # stop processing
            break
        # push result onto queue
        queue_out.put(response)


def parse_page(queue_in, queue_out, barrier) -> None:
    # loop forever
    while True:
        # read item from queue
        data = queue_in.get()
        # check for shutdown
        if data is None:
            # put signal back on queue
            queue_in.put(None)
        	# wait on the barrier for all other workers
            barrier.wait()
            # send signal on output queue
            queue_out.put(None)
            # stop processing
            break
        #
        parsed_data = backend.parse(data)
        # push result onto queue
        queue_out.put(parsed_data)


def thread_get_and_parse(token) -> pd.DataFrame:
    # create the shared queues
    task1_queue_in = queue.Queue()
    task1_queue_out = queue.Queue()
    task2_queue_out = queue.Queue()
    #
    barrier1 = threading.Barrier(5)
    barrier2 = threading.Barrier(10)
    #
    results = []
    i = 1
    # create the thread pool
    with st.spinner():
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as threadpool:
            # issue task 1 workers
            _ = [threadpool.submit(backend.get_activities_page, task1_queue_in, task1_queue_out, barrier1, token)
                 for _ in range(5)]
            # issue task 2 workers
            _ = [threadpool.submit(backend.parse_page, task1_queue_out, task2_queue_out, barrier2)
                 for _ in range(10)]
            for thread in threadpool._threads:
                st.runtime.scriptrunner.add_script_run_ctx(thread)
            # push work into task 1
            while True:
                st.write(f"{i=}")
                task1_queue_in.put(i)
                i += 1
                time.sleep(1)
                if None in task1_queue_in.queue:
                    # signal that there is no more work
                    task1_queue_in.put(None)
                    st.write("Breaking loop")
                    break
            # consume results
            while True:
                # retrieve data
                data = task2_queue_out.get()
                st.write("Retrieved element from queue")
                # check for the end of work
                if data is None:
                    # stop processing
                    st.write("Breaking loop")
                    break
                # <>
                results.append(data)
                st.write(len(results), results[-1])
    total = pd.concat(results)
    return total

if __name__ == "__main__":
    pass
