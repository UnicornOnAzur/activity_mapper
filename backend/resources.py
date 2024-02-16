# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""
# Third party
import plotly.express as px
# Local imports
import backend.utils as bu

# text
CAPTION = \
    "This page was created by QtyPython2020 and the code can be found on https://github.com/QtyPython2020/activity_mapper ."
EXPLANATION = """To use this dashboard click on "Connect with Strava". This will redirect you to the Strava page. Then select to view public and/or private activities, and click "Authorize". This provides the dashboard with your data for the duration of your use."""
ERROR_MESSAGE = "An error occurred while retrieving the data. Please try to authorize again."
TITLE = "Activity Mapper"
# column lists
DISPLAY_COLS = ["name",
                "view on Strava",
                "date",
                "type", "sport_type", "country"]
STRAVA_COLS = ["app", "weekday", "time", "hour", "minutes", "name", "date","country"]
# config dicts
CONFIG = {"displaylogo": False,
          "displayModeBar": False,}
CONFIG2 = {"displaylogo": False,
           "modeBarButtonsToRemove": ["pan2d",
                                      "lasso2d",
                                      "select2d",
                                      "toImage",
                                      "zoom2d",
                                      "autoscale"]}

# paths
PATH_MAPPER = "strava_categories.txt"
# colors and themes
COLOR_MAP = {"Strava": "#FC4C02",  # the color of the Strava app
             }
DISCRETE_COLOR = px.colors.sequential.Oranges_r
TEMPLATE = "plotly_dark"
# sizes
LEFT_RIGHT_MARGIN = 20
TOP_BOTTOM_MARGIN = 25
TOP_ROW_HEIGHT = 200
BOTTOM_ROW_HEIGHT = 600
# urls
AUTH_LINK = "https://www.strava.com/oauth/token"
# external data
geojson_file = bu.get_request("https://datahub.io/core/geo-countries/r/0.geojson")


if __name__ == "__main__":
    pass
