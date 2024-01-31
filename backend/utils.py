# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""
# Standard library
import base64
# Third party
import requests


def load_mapper(path: str) -> dict:
    with open(path, mode="r") as file:
        mapper: dict = {value.strip():main
                        for main, values in [[el for el in part.split("\n\n")]
                                             for part in file.read().split("\n\n\n") ]
                        for value in values.split("\n") if value.strip() != ""}
    return mapper


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
        The amount of seconds before closing the connection. The default is 5.

    Returns
    -------
    dict
        DESCRIPTION.

    """
    result: dict = {}
    response = requests.post(url=url,
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
        The amount of seconds before closing the connection. The default is 5.

    Returns
    -------
    dict
        DESCRIPTION.

    """
    result: dict = {}
    response = requests.get(url=url,
                            params=params,
                            headers=headers,
                            timeout=timeout)
    if response.ok:
        result: dict = response.json()
    else:
        result.update({str(response.status_code): response.reason})
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


if __name__ == "__main__":
    pass
