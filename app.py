# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""
# Standard library
import sys
# Third party
import pandas as pd
import streamlit as st
from streamlit.elements.utils import _shown_default_value_warning
# Local imports
import charts
import get_data
import strava_parser
import utils


TITLE = "Activity Mapper"
COLS_STRAVA = ["timestamp",  # used in the area and bar chart
               "year", # used in the area chart
               "week", # used in the area chart
               "calender-week", # used in the area chart
               "weekday", # used in the bar chart
               "date", # used in the area chart and the map
               "time", # used in the area chart
               "hour", # used in polar chart
               "minutes", # used in polar chart
               "name", # used in the area chart and the map
               "lat", "lon", # used in the map
               "app", # used in all charts
               "sport_type", # used in pie chart
               "coords" # used in the map
               ]
with open("../instructions.txt", mode="r", encoding="utf-8") as file:
    STRAVA_TEXT = file.readline()
# suppress the warning about the slider value being set on initialization
_shown_default_value_warning = False
# configure the toolbar on the plotly tools
config = {"displayModeBar": True,
          "displaylogo": False,
          "modeBarButtonsToRemove": ["pan2d",
                                     "lasso2d",
                                     "select2d",
                                     "toImage"],
          # TODO: customize toolbar to add zoom button
          "modeBarButtonsToAdd": ["zoom2d",
                                  "scrollZoom"]
          }
config_none = {"displayModeBar": False,
               "displaylogo": False,}
#


def connect_strava() -> None:
    """


    Returns
    -------
    None
        DESCRIPTION.

    """
    error_message = st.empty()
    # RETREIVING THE ACCESS TOKEN
    progress_bar = st.progress(0, "Getting access token")
    inputs = st.session_state.get("id"),\
        st.session_state.get("secret"), st.session_state.get("refresh")
    access_token = get_data.request_access_token(*inputs)
    # RETREIVING THE DATA
    progress_bar.progress(10, "Retreiving data...")
    data = get_data.request_data_from_api(access_token)
    # PARSING THE DATA
    progress_bar.progress(80, "Parsing data...")
    if list(data[0].keys()) == ["message","errors"]:
        # if an error occur stop the function
        error_message = st.error(f"An error occurred while retrieving the data. {data[0]}")
        return
    st.session_state["dataframe"] = strava_parser.parse(data)
    # FINALIZE THE PROCRESS
    progress_bar.progress(100, "Done")
    dataframe = st.session_state.get("dataframe")
    st.session_state["time_range"] = utils.get_min_max_time(dataframe)
    progress_bar.empty()
    return


def filter_df() -> None:
    """


    Returns
    -------
    None
        DESCRIPTION.

    """
    with st.spinner("filtering..."):
        dataframe = st.session_state.get("dataframe",
                                         pd.DataFrame(columns=COLS_STRAVA,
                                                      dtype="object")
                                         )
        begin_date, end_data = st.session_state.get("time_range",
                                                    utils.get_min_max_time(dataframe))
        st.session_state["filtered_dataframe"] = dataframe.loc[(dataframe["date"] >= begin_date) &
                                                               (dataframe["date"] <= end_data),
                                                               COLS_STRAVA]


def reset_time_slider():
    """


    Returns
    -------
    None.

    """
    if st.session_state.get("reset"):
        dataframe = st.session_state.get("dataframe")
        st.session_state["time_range"] = utils.get_min_max_time(dataframe)


def main() -> None:
    """


    Parameters
    ----------
    None

    Returns
    -------
    None

    """
    # INITIALIZATION
    intervals = 100
    height1 = intervals * 3.5
    height2 = height1 * 2
    filter_df()
    data = st.session_state.get("filtered_dataframe",
                                pd.DataFrame(columns=COLS_STRAVA,
                                             dtype="object")
                                )
    with st.spinner("Making visualizations."):
        # SIDEBAR
        with st.sidebar:
            st.header("Menu")
            # GENERAL SECTION
            if st.session_state.get("dataframe") is not None:
                st.info("Strava data has been loaded")
                    # set the sidebar state to collapsed so that it will automatically fold
                st.session_state["sidebar_state"] = "collapsed"
            st.button("Reset time slider",
                      help="Click to reset the time slider to the entire time range",
                      on_click=reset_time_slider,
                      key="reset")
            # STRAVA SECTION
            st.divider()
            st.subheader("Strava")
            st.write(STRAVA_TEXT)
            #TODO: verify input
            st.session_state["id"] = st.text_input("Strava ID",
                                                   max_chars=6, # the length of the Strava ID
                                                   type="password", # hide user input
                                                   help="The number sequence listed\
                                                       under 'Client ID'"
                                                   )
            if (client_id:=st.session_state.get("id")):
                if len(client_id) < 4:
                    st.error("The client ID is not of the correct length")
            st.session_state["secret"] = st.text_input("Secret code",
                                                       max_chars=40, # the length of the secret code
                                                       type="password", # hide user input
                                                       help="The sequence listed\
                                                           under 'Client Secret'"
                                                       )
            if (client_id:=st.session_state.get("id")):
                if len(client_id) < 4:
                    st.error("The client ID is not of the correct length")
            st.session_state["refresh"] = st.text_input("Refresh token",
                                                       max_chars=40, # the length of the secret code
                                                       type="password", # hide user input
                                                       help="The sequence listed under\
                                                           'Your Refresh Token'"
                                                       )
            if (client_id:=st.session_state.get("id")):
                if len(client_id) < 4:
                    st.error("The client ID is not of the correct length")
            # if all the inputs are provided show the connect button
            if st.session_state.get("id") and st.session_state.get("secret") \
                and st.session_state.get("refresh"):
                    #TODO replace button with Strava logo
                st.button("Connect with Strava",
                          help="Click to retreive the data from Strava",
                          on_click=connect_strava,
                          key="strava_connect")
            # EMPTY SECTION
            st.divider()

        # MAIN PAGE
        with st.container():
            st.header(TITLE)
            # CREATE THE PANELS
            left, right = st.columns(spec=[6,6],
                                     gap="small")
            # RIGHT PANEL
            right.plotly_chart(charts.locations(data.loc[:],
                                             height2),
                            use_container_width=True,
                            config = config
                            )
            # LEFT PANEL
            left.plotly_chart(charts.timeline(data.loc[:,["app",
                                                          "timestamp",
                                                          "time",
                                                          "name",
                                                          "date",
                                                          "year",
                                                          "week",
                                                          "calender-week"]],
                                                height1),
                                use_container_width=True,
                                config = config_none
                                )
            cols = left.columns([2,1,1])
            cols[0].plotly_chart(charts.days(data.loc[:],
                                             height1),
                                 use_container_width=True,
                                 config = config_none
                                 )
            cols[1].plotly_chart(charts.hours(data.loc[:],
                                              height1),
                                 use_container_width=True,
                                 config = config_none
                                 )
            cols[2].plotly_chart(charts.types(data.loc[:],
                                              height1),
                                 use_container_width=True,
                                 config = config_none
                                 )

        # SLIDER
        # with st.container():
            # st.select_slider(label="Select a timeframe",
            #                   options=utils.get_time_range(st.session_state.get("dataframe")),
            #                   value=utils.get_min_max_time(st.session_state.get("dataframe")),
            #                   key="time_range",
            #                   help="Select a time period to display",
            #                   on_change=filter_df,
            #                   )

if __name__ == "__main__":
    # set the initial state of the sidebar
    if "sidebar_state" not in st.session_state:
        st.session_state["sidebar_state"] = "expanded"
    st.set_page_config(page_title=TITLE,
                       page_icon=":world_map:",
                       layout="wide",
                       initial_sidebar_state=st.session_state.get("sidebar_state")
                       )
    main()
