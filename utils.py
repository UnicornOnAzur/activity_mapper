# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""
# Standard library
import datetime
# Third party
import numpy as np
import pandas as pd


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


def determine_zoom(latitudes: list[float],
                   longitudes: list[float]) -> int:
    """


    Parameters
    ----------
    longitudes : list[float]
        DESCRIPTION.
    latitudes : list[float]
        DESCRIPTION.

    Returns
    -------
    int
        DESCRIPTION.

    """
    #
    if latitudes == []:
        latitudes, longitudes = [[0],[0]]
    height = max(latitudes)- min(latitudes)
    width = max(longitudes)- min(longitudes)
    area = height * width
    zoom = int(round(np.interp(x=area,
                               xp=[0, 5**-10, 4**-10, 3**-10, 2**-10, 1**-10, 1**-5],
                               fp=[20, 15,    14,     13,     12,     7,      1]
                               )+10**-5
                     )
               )
    return zoom

if __name__ == "__main__":
    pass
