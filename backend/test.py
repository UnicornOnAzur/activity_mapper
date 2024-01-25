# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""
import json

def load_test_data() -> dict:
    """
    Load the sample data from the Strava API documentation.

    Returns
    -------
    data: dict
        DESCRIPTION.

    """
    with open("api_test.txt", "rb") as file:
        data: dict = json.loads(file.read())
    return data

if __name__ == "__main__":
    pass
