# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""
# Standard library
import base64
import datetime
import requests
# Third party
import pandas as pd

def post_request(url: str,
                 params: dict = None,
                 timeout: int = 5) -> dict:
    """


    Parameters
    ----------
    url : str
        DESCRIPTION.

    Returns
    -------
    dict
        DESCRIPTION.

    """
    result: dict = {}
    response = requests.post(url=url,
                             params=params,
                             timeout=timeout)
    if response.ok:
        result: dict = response.json()
    return result


def get_request(url: str,
                params: dict,
                headers: dict,
                timeout: int = 5) -> dict:
    """


    Parameters
    ----------
    url : str
        DESCRIPTION.

    Returns
    -------
    dict
        DESCRIPTION.

    """
    result: dict = {}
    response = requests.get(url=url,
                            params=params,
                            headers=headers)
    if response.ok:
        result: dict = response.json()
    return result


def load_image(path: str) -> str:
    """


    Parameters
    ----------
    path : str
        DESCRIPTION.

    Returns
    -------
    str
        DESCRIPTION.

    """
    with open(path, "rb") as file:
        contents: bytes = file.read()
    image_as_str: str = base64.b64encode(contents).decode("utf-8")
    return image_as_str


def min2ang(time: int) -> int:
    """


    Parameters
    ----------
    hour : int
        DESCRIPTION.
    minute : int
        DESCRIPTION.

    Returns
    -------
    int
        DESCRIPTION.

    """
    hour, minute = time//60, time%60
    angle = (hour * 15) % 360 + minute * 2.5
    return angle


def hr2ang(hour: int) -> int:
    """


    Parameters
    ----------
    hour : int
        DESCRIPTION.

    Returns
    -------
    int
        DESCRIPTION.

    """
    angle = (hour * 15) % 360
    return angle


def get_time_range(dataframe: pd.DataFrame) -> tuple[datetime.datetime]:
    """


    Parameters
    ----------
    dataframe : pd.DataFrame
        DESCRIPTION.

    Returns
    -------
    dates : TYPE
        DESCRIPTION.

    """
    # get the current date
    today = datetime.datetime.today()
    if dataframe is None or dataframe.empty:
        # if no date can be derived take a week as the period
        begin_date = today - datetime.timedelta(days=9)
    else:
        begin_date = dataframe.date.min()

    # make a date range in steps of weeks
    date_range = pd.date_range(start=begin_date,
                               end=today,
                               freq="W", # calendar frequency by week
                               inclusive="both", # include begin and end date in the range
                               )
    # convert list of DatetimeIndexes to a list of datetime objects
    dates = list(map(lambda d:d.date(),
                     date_range))
    return dates


def get_min_max_time(dataframe: pd.DataFrame) -> tuple[datetime.datetime]:
    """
    Return a tuple of the minimum and maximum date

    Parameters
    ----------
    dataframe : pd.DataFrame
        DESCRIPTION.

    Returns
    -------
    tuple
        DESCRIPTION.

    """
    date_range = get_time_range(dataframe)
    return min(date_range), max(date_range)


if __name__ == "__main__":
    pass
