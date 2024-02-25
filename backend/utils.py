# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

Helper functions for the activity mapper app.
"""
# Standard library
import base64
import collections
# Third party
import requests
import urllib3


def post_request(url: str,
                 data: dict = None,
                 timeout: int = 60) -> dict:
    """
    Wrapper for the post request that always returns a dictionary.

    Parameters
    ----------
    url : str
        The requested url.
    params : dict, optional
        The payload. The default is None.
    timeout : int, optional
        The amount of seconds before closing the connection. The default is 60.

    Returns
    -------
    result: dict
        The json response as a dictionary or an empty dictionary.

    """
    result: dict = {}
    response: requests.Response = requests.post(url=url,
                                                data=data,
                                                timeout=timeout)
    if response.ok:
        result: dict = response.json()
    else:
        result.update({str(response.status_code): response.reason})
    return result


def get_request(url: str,
                params: dict = None,
                headers: dict = None,
                timeout: int = 60) -> dict:
    """
    Wrapper for the get request that always returns a dictionary.

    Parameters
    ----------
    url : str
        The requested url.
    params : dict, optional
        The query string elements. The default is None.
    headers : dict, optional
        The HTTP headers. The default is None.
    timeout : int, optional
        The amount of seconds before closing the connection. The default is 60.

    Returns
    -------
    dict
        The json response as a dictionary or an empty dictionary.

    """
    result: dict = {}
    session = requests.Session()
    retry = urllib3.Retry(total=4,
                          backoff_factor=1,
                          allowed_methods=None,
                          status_forcelist=[429, 500, 502, 503, 504]
                          )
    adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    response: requests.Response = session.get(url=url,
                                               params=params,
                                               headers=headers,
                                               timeout=timeout)
    if response.ok:
        result: dict = response.json()
    else:
        result.update({str(response.status_code): response.reason})
    return result


def load_category_mapper(path: str) -> collections.defaultdict:
    """
    Load the different sport types with their categories into a dictionary.

    Parameters
    ----------
    path : str
        Filepath of the textfile with the categories.

    Returns
    -------
    mapper: collections.defaultdict
        A dictionary to map all activities to their categories.

    """
    def corrected(key: str) -> str:
        """


        Parameters
        ----------
        key : str
            DESCRIPTION.

        Returns
        -------
        str
            DESCRIPTION.

        """
        corrections: dict = {"E-Bike Ride": "EBikeRide",
                             "E-Mountain Bike Ride": "EMountainBikeRide",
                             "Kayak": "Kayaking",
                             "Stair Stepper": "StairStepper",
                             "Surf": "Surfing",
                             "Weight Training": "WeightTraining"}
        correction: str = corrections.get(key, key)
        return correction


    with open(path, mode="r") as file:
        original: dict = {corrected(value.strip()): main
                          for main, values in [part.split("\n\n")
                                               for part
                                               in file.read().split("\n\n\n")
                                               ]
                          for value in values.split("\n")
                          if value.strip() != ""
                          }
    mapper: collections.defaultdict = collections.defaultdict(str, original)
    return mapper


def load_country_code_mapper(path: str):
    """


    Parameters
    ----------
    path : str
        DESCRIPTION.

    Returns
    -------
    mapper : TYPE
        DESCRIPTION.

    """
    with open(path, mode="r") as file:
        mapper: dict = {row[1].strip(): row[0].strip()
                        for row in map(lambda line: line.split("\t"),
                                      file.readlines()
                                      )
                        }
    return mapper

def load_image(path: str) -> str:
    """
    Load an image into a string representation for use in markdown.

    Parameters
    ----------
    path : str
        The filepath of the image.

    Returns
    -------
    image_as_str: str
        The string representation.

    """
    with open(path, "rb") as file:
        contents: bytes = file.read()
    image_as_str: str = base64.b64encode(contents).decode("utf-8")
    return image_as_str


def min2ang(time: int) -> float:
    """
    Calculate the angle of the time in minutes for the polar plot.

    Parameters
    ----------
    time : int
        The time of the activity.

    Returns
    -------
    angle: float
        The angle.

    """
    hour, minute = time//60, time % 60
    angle: float = (hour * 15) % 360 + minute * 2.5
    return angle


def hr2ang(hour: int) -> int:
    """
    Calculate the angle of the time in hours for the polar plot.

    Parameters
    ----------
    time : int
        The time of the activity.

    Returns
    -------
    angle: float
        The angle.

    """
    angle: int = (hour * 15) % 360
    return angle


if __name__ == "__main__":
    pass
