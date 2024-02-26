# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""
# Third party
import json


def load_test_data() -> list[dict]:
    """
    Load the sample data from the Strava API documentation.
    Returns
    -------
    data: dict
        DESCRIPTION.
    """
    with open("api_test.txt", "rb") as file:
        data: list[dict] = json.loads(file.read())
    new_data = []
    for element in data:
        element.update({"country":None})
        new_data.append(element)
    return data


if __name__ == "__main__":
    pass