# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""
# Third party
import plotly.express as px
# Local imports
import backend

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
AUTH_LINK: str = "https://www.strava.com/oauth/token"
ACTIVITIES_LINK: str = "https://www.strava.com/api/v3/athlete/activities"
NOMINATIM_LINK: str = "https://nominatim.openstreetmap.org/reverse"

# JSON
GEOJSON: dict = backend.get_request(
    "https://datahub.io/core/geo-countries/r/0.geojson"
                                    )


if __name__ == "__main__":
    pass
