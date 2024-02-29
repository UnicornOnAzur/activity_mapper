# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""
#  Standard library
import os
# Third party
import plotly.express as px
# Local imports
import backend

#
STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")

# TEXT
CAPTION: str = \
    """
This page was created by QtyPython2020 and the code can be found on
https://github.com/QtyPython2020/activity_mapper .
"""
EXPLANATION: str =\
    """
To use this dashboard click on "Connect with Strava". This will redirect you to
the Strava page. Then select to view public and/or private activities, and
click "Authorize". This provides the dashboard with your data for the duration
of your use.
"""
ERROR_MESSAGE: str =\
    """
An error occurred while retrieving the data. Please try to authorize again.
"""
TITLE: str = "Activity Mapper"

# COLUMNS FOR DATAFRAMA
DISPLAY_COLS: list[str] = ["name",
                           "view on Strava",
                           "date",
                           "type",
                           "sport_type",
                           "country"]
STRAVA_COLS: list[str] = ["app",
                          "weekday",
                          "time",
                          "hour",
                          "minutes",
                          "name",
                          "date",
                          "country",
                          "lat",
                          "lon"]

# DICT WITH CONFIGURATION FOR PLOTLY CHARTS
CONFIG: dict = {"displaylogo": False,  # remove the plotly logo
                "displayModeBar": False  # modebar never visible
                }
CONFIG2: dict = {"displaylogo": False,  # remove the plotly logo
                 "modeBarButtonsToRemove":  # remove buttons from modebar
                 ["pan2d",  # pan button
                  "toImage",  # download button
                  ]
                 }

# FILE PATHS
PATH_CODES: str = "country_codes.txt"
PATH_MAPPER: str = "strava_categories.txt"

# COLORS AND THEMES
COLOR_MAP: dict = {"Strava": "#FC4C02"}  # the color of the Strava app
DISCRETE_COLOR: list[str] = px.colors.sequential.Oranges_r
TEMPLATE: str = "plotly_dark"

# SIZES FOR PLOTS
LEFT_RIGHT_MARGIN: int = 20
TOP_BOTTOM_MARGIN: int = 25
TOP_ROW_HEIGHT: int = 200
BOTTOM_ROW_HEIGHT: int = 600

# URLS
APP_URL: str = "https://strava-activity-mapper.streamlit.app/"
TOKEN_LINK: str = "https://www.strava.com/oauth/token"
AUTH_LINK: str = "https://www.strava.com/oauth/authorize"
ACTIVITIES_LINK: str = "https://www.strava.com/api/v3/athlete/activities"
ACTIVITIES_URL: str = "https://www.strava.com/activities/"
NOMINATIM_LINK: str = "https://nominatim.openstreetmap.org/reverse"
authorization_link = f"""
{AUTH_LINK}?client_id={STRAVA_CLIENT_ID}&response_type=code&redirect_uri={APP_URL}&approval_prompt=force&scope=activity:read,activity:read_all
"""

# JSON
GEOJSON: dict = backend.get_request(
    "https://datahub.io/core/geo-countries/r/0.geojson"
                                    )


if __name__ == "__main__":
    pass
