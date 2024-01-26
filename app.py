# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

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
BOTTOM_ROW_HEIGHT = 500
APP_URL = os.environ.get("APP_URL")
STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")
STRAVA_COLS = ["app", "weekday", "time", "hour", "minutes", "name"]
DISPLAY_COLS = ["name", "date", "type", "sport_type", "view on Strava"]
authorization_link = f"https://www.strava.com/oauth/authorize?client_id={STRAVA_CLIENT_ID}&response_type=code&redirect_uri={APP_URL}&approval_prompt=force&scope=activity:read_all"
AUTH_LINK = "https://www.strava.com/oauth/token"

def get_access_token(authorization_code):
    res = bu.post_request(AUTH_LINK,
                          params={"client_id":STRAVA_CLIENT_ID,
                                  "client_secret": STRAVA_CLIENT_SECRET,
                                  "code": authorization_code,
                                  "grant_type": "authorization_code"})
    athlete_name = " ".join((res.get("athlete", {}).get("firstname", ""),
                             res.get("athlete", {}).get("lastname", "")
                             )
                            )
    refresh_token = res.get("refresh_token")
    access_token = res.get("access_token")
    return athlete_name, access_token, refresh_token


def connect_strava(code):
    error_message = st.empty()
    # RETREIVING THE ACCESS TOKEN
    progress_bar = st.progress(0, "Getting access token")
    results = get_access_token(code)
    st.session_state["athlete_name"] = results[0]
    st.session_state["access_token"] = results[1]
    st.session_state["refresh_token"] = results[2]
    # RETREIVING THE DATA
    progress_bar.progress(33, "Retreiving data...")
    data = bsp.request_data_from_api(st.session_state["access_token"])
    # PARSING THE DATA
    progress_bar.progress(67, "Parsing data...")
    if list(data[0].keys()) == ["message","errors"]:
        # if an error occur stop the function
        error_message = st.error(f"An error occurred while retrieving the data. {data[0]}")
        return
    st.session_state["dataframe"] = (dataframe:= bsp.parse(data))
    st.session_state["time_range"] = bu.get_min_max_time(dataframe)
    # FINALIZE THE PROCRESS
    progress_bar.progress(100, "Done")
    # dataframe = st.session_state.get("dataframe")
    progress_bar.empty()
    return


def main():
    params: dict = st.query_params.to_dict()
    code = params.get("code")
    if code:
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
            st.divider()
            if not st.session_state.get("athlete_name"):
                image_connect = bu.load_image("logos/btn_strava_connectwith_orange@2x.png")
                st.markdown(f'<a href="{authorization_link}">'
                            f'<img src="data:image/png;base64,{image_connect}" width="100%">'
                            f'</a>',
                            unsafe_allow_html=True)
            else:
                st.info("connected")
                st.session_state["sidebar_state"] = "collapsed"
            st.divider()
            st.markdown(body=open("intro.txt").read())
            st.divider()
            test = st.button("Use test data")
            if test:
                st.session_state["dataframe"] = bsp.parse(bt.load_test_data())

        # MAIN PAGE
        with st.container():
            st.subheader(": ".join([TITLE, welcome_text]))
            # top row
            st.plotly_chart(figure_or_data=bpc.timeline(df,
                                                        TOP_ROW_HEIGHT),
                               use_container_width=True)

        with st.container():
            # middle row
            st.divider()
            cols = st.columns(spec=[6,6],
                              gap="small")
            cols[0].plotly_chart(figure_or_data=bpc.days(df,
                                                          BOTTOM_ROW_HEIGHT/2),
                                  use_container_width=True)
            cols[1].plotly_chart(figure_or_data=bpc.locations(df,
                                                         BOTTOM_ROW_HEIGHT),
                                 use_container_width=True)
            subcols = cols[0].columns(spec=[3,3], gap="small")
            subcols[0].plotly_chart(figure_or_data=bpc.types(df,
                                                          BOTTOM_ROW_HEIGHT/2),
                                  use_container_width=True)
            subcols[1].plotly_chart(figure_or_data=bpc.hours(df,
                                                          BOTTOM_ROW_HEIGHT/2),
                                  use_container_width=True)
            st.divider()
            # SLIDER
        with st.expander("See unique events", expanded = False):
            st.dataframe(data=st.session_state.get("dataframe", pd.DataFrame(columns=DISPLAY_COLS)).loc[:, DISPLAY_COLS],
                         use_container_width=True,
                         hide_index=True,
                         column_order=DISPLAY_COLS,
                         column_config={"view on Strava": st.column_config.LinkColumn(label=None,
                                                                                      help="See this activity on the Strava website")
                                        }
                         )


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
