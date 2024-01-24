# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""
# Standard library
import os
import requests
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

authorization_link = f"https://www.strava.com/oauth/authorize?client_id={STRAVA_CLIENT_ID}&response_type=code&redirect_uri={APP_URL}&approval_prompt=force&scope=activity:read_all"


def get_access_token(authorization_code):
    other_link = f"https://www.strava.com/oauth/token?client_id={STRAVA_CLIENT_ID}&client_secret={STRAVA_CLIENT_SECRET}&code={authorization_code}&grant_type=authorization_code"
    res = bu.post_request(other_link)
    st.session_state["athlete_name"] = " ".join((res.get("athlete", {}).get("firstname"),
                                                 res.get("athlete", {}).get("lastname")))
    st.session_state["refresh_token"] = res.get("refresh_token")
    st.session_state["access_token"] = res.get("access_token")


def request_data_from_api(access_token: str) -> list[dict]:
    """
    Send get requests in a loop to retreive all the activities. Loop will stop if
    the result is empty implying that all activities have been retrieved.

    Parameters
    ----------
    access_token : str
        DESCRIPTION.

    Returns
    -------
    list[dict]
        DESCRIPTION.

    """
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    header = {"Authorization": f"Bearer {access_token}"}
    request_page_num = 1
    all_activities = []

    while True:
        param = {"per_page": 200,
                 "page": request_page_num}
        response = requests.get(activities_url,
                                headers=header,
                                params=param)
        data_set = response.json()
        print(request_page_num, response.status_code, type(data_set))
        if not response.ok:
            all_activities.append(data_set)
            return all_activities
        # break out of the loop if the response is empty
        if len(data_set) == 0:
            break
        # add onto the list
        if all_activities:
            all_activities.extend(data_set)
        # populate the list if it is empty
        else:
            all_activities = data_set
        # increment to get the next page
        request_page_num += 1
    return all_activities

def connect_strava(code):
    error_message = st.empty()
    # RETREIVING THE ACCESS TOKEN
    progress_bar = st.progress(0, "Getting access token")
    get_access_token(code)
    # RETREIVING THE DATA
    progress_bar.progress(10, "Retreiving data...")
    data = request_data_from_api(st.session_state["access_token"])
    # PARSING THE DATA
    progress_bar.progress(80, "Parsing data...")
    if list(data[0].keys()) == ["message","errors"]:
        # if an error occur stop the function
        error_message = st.error(f"An error occurred while retrieving the data. {data[0]}")
        return
    st.session_state["dataframe"] = bsp.parse(data)
    # FINALIZE THE PROCRESS
    progress_bar.progress(100, "Done")
    dataframe = st.session_state.get("dataframe")
    st.session_state["time_range"] = bu.get_min_max_time(dataframe)
    progress_bar.empty()
    return


def main():
    params: dict = st.query_params.to_dict()
    code = params.get("code")
    welcome_text = "Welcome" if not (n:=st.session_state.get('athlete_name')) else f"Welcome, {n}"
    if code:
        connect_strava(code)
    df = st.session_state.get("dataframe",
                              pd.DataFrame(columns=["app", "weekday", "time", "hour", "minutes", "name"]))
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

        # MAIN PAGE
        with st.container():
            st.subheader(TITLE)
            st.subheader(welcome_text)
            # top row
            st.plotly_chart(figure_or_data=bpc.timeline(df,
                                                        TOP_ROW_HEIGHT),
                               use_container_width=True)

        with st.container():
            # middle row
            st.divider()
            cols = st.columns(spec=[2,2,2,6],
                              gap="small")
            cols[0].plotly_chart(figure_or_data=bpc.types(df,
                                                          BOTTOM_ROW_HEIGHT),
                                 use_container_width=True)
            cols[1].plotly_chart(figure_or_data=bpc.hours(df,
                                                          BOTTOM_ROW_HEIGHT),
                                 use_container_width=True)
            cols[2].plotly_chart(figure_or_data=bpc.days(df,
                                                         BOTTOM_ROW_HEIGHT),
                                 use_container_width=True)
            cols[3].plotly_chart(figure_or_data=bpc.locations(df,
                                                         BOTTOM_ROW_HEIGHT),
                                 use_container_width=True)
        with st.container():
            st.divider()
            st.write(st.session_state)
            st.dataframe(st.session_state.get("dataframe"))


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
