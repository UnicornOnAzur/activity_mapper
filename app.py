# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

<>
"""
# Standard library
import os
# Third party
import pandas as pd
import streamlit as st
# Local imports
import backend.plotly_charts as bpc
import backend.strava_parser as bsp
import backend.test as bt
import backend.utils as bu


TITLE = "Activity Mapper"
TOP_ROW_HEIGHT = 200
BOTTOM_ROW_HEIGHT = 600
STRAVA_COLS = ["app", "weekday", "time", "hour", "minutes", "name"]
DISPLAY_COLS = ["name", "date", "type", "sport_type", "view on Strava"]
CONFIG = {"displaylogo": False,
          "displayModeBar": False,}
CONFIG2 = {"displaylogo": False,
           "modeBarButtonsToRemove": ["pan2d",
                                      "lasso2d",
                                      "select2d",
                                      "toImage",
                                      "zoom2d",
                                      "autoscale"]}
EXPLANATION = """To use this dashboard click on "Connect with Strava". This will redirect you to the Strava page. Then select to view public and/or private activities, and click "Authorize". This provides the dashboard with your data for the duration of your use."""
ERROR_MESSAGE = "An error occurred while retrieving the data. Please try to authorize again."

APP_URL = os.environ.get("APP_URL")
STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
authorization_link = "https://www.strava.com/oauth/authorize"+\
    f"?client_id={STRAVA_CLIENT_ID}&response_type=code&"+\
    f"redirect_uri={APP_URL}&approval_prompt=force&"+\
    "scope=activity:read,activity:read_all"


def connect_strava(code: str):
    """
    <>

    Parameters
    ----------
    code : str
        The authorization code from the previous request to the Strava API.

    Returns
    -------
    None.

    """
    error_message = st.empty()
    # RETREIVING THE ACCESS TOKEN
    progress_bar = st.progress(0, "Getting access token")
    results = bsp.get_access_token(code)
    st.session_state["athlete_name"] = results[0]
    st.session_state["access_token"] = results[1]
    st.session_state["refresh_token"] = results[2]
    st.session_state["creation"] = results[3]
    # RETREIVING THE DATA
    progress_bar.progress(33, "Retreiving data...")
    data = bsp.request_data_from_api(st.session_state["access_token"])
    # PARSING THE DATA
    progress_bar.progress(67, "Parsing data...")
    # if an error occur stop the function
    if data[0] == {'401': 'Unauthorized'}:
        error_message = st.error(ERROR_MESSAGE)
        return
    st.session_state["dataframe"] = bsp.parse(data)
    # FINALIZE THE PROCESS
    progress_bar.progress(100, "Done")
    progress_bar.empty()
    wrap_up()
    return


def wrap_up():
    """
    <>

    Returns
    -------
    None.

    """
    # set the sidebar to collapse after the rerun
    st.session_state["sidebar_state"] = "collapsed"
    # signal that data has been loaded
    st.session_state["loaded"] = True
    # rerun the page to have header and sidebar be updated
    st.rerun()


def main():
    """
    <>

    Returns
    -------
    None.

    """
    params: dict = st.query_params.to_dict()
    code = params.get("code")
    if code and not st.session_state.get("loaded", False):
        connect_strava(code)
    welcome_text = "Welcome" if not (n:=st.session_state.get('athlete_name')) else f"Welcome, {n}"
    df = st.session_state.get("dataframe",
                              pd.DataFrame(columns=STRAVA_COLS))
    with st.spinner("Making visualizations..."):
        # sidebar
        with st.sidebar:
            image_powered = bu.load_image("logos/api_logo_pwrdBy_strava_horiz_light.png")
            st.markdown(f'<img src="data:image/png;base64,{image_powered}" width="100%">',
                        unsafe_allow_html=True)
            st.header("Menu")
            if not st.session_state.get("loaded"):
                image_connect = bu.load_image("logos/btn_strava_connectwith_orange@2x.png")
                st.markdown(f'<a href="{authorization_link}">'
                            f'<img src="data:image/png;base64,{image_connect}" width="100%">'
                            f'</a>',
                            unsafe_allow_html=True)
            else:
                st.error("connected")
            st.divider()
            st.markdown(EXPLANATION)
            if st.button("Show with demo data"):
                st.session_state["dataframe"] = bsp.parse(bt.load_test_data())
                wrap_up()

        # MAIN PAGE
        with st.container():
            st.markdown(f"## {TITLE}: {welcome_text}")
            # top row
            st.plotly_chart(figure_or_data=bpc.timeline(df,
                                                        TOP_ROW_HEIGHT,
                                                        creation=st.session_state.get("creation")),
                               use_container_width=True,
                               config=CONFIG)

        with st.container():
            # middle row
            cols = st.columns(spec=[6,6],
                              gap="small")
            cols[0].plotly_chart(figure_or_data=bpc.days(df,
                                                         BOTTOM_ROW_HEIGHT//3-50),
                                  use_container_width=True,
                                  config=CONFIG)
            cols[1].plotly_chart(figure_or_data=bpc.locations(df,
                                                              BOTTOM_ROW_HEIGHT),
                                 use_container_width=True,
                                 config=CONFIG2)
            subcols = cols[0].columns(spec=[3,3], gap="small")
            subcols[0].plotly_chart(figure_or_data=bpc.types(df,
                                                             BOTTOM_ROW_HEIGHT//1.5),
                                  use_container_width=True,
                                  config=CONFIG)
            subcols[1].plotly_chart(figure_or_data=bpc.hours(df,
                                                             BOTTOM_ROW_HEIGHT//1.5),
                                  use_container_width=True,
                                  config=CONFIG)
            # SLIDER
        with st.expander("See unique events", expanded = False):
            st.dataframe(data=st.session_state.get("dataframe",
                                                   pd.DataFrame(columns=DISPLAY_COLS)
                                                   ).loc[:, DISPLAY_COLS],
                         use_container_width=True,
                         hide_index=True,
                         column_order=DISPLAY_COLS,
                         column_config={"view on Strava":
                                        st.column_config.LinkColumn(label=None,
                                                                    help=\
                                        "See this activity on the Strava website")
                                        }
                         )
        st.caption("This page was created by QtyPython2020. The code can be found on https://github.com/QtyPython2020/activity_mapper .")


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
