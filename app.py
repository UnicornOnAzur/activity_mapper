# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""
# Standard library
import requests
import os
# Third party
import pandas as pd
import streamlit as st
# Local imports
import backend.plotly_charts as bpc
import backend.strava_parser as bsp
import backend.utils as bu

TITLE = "Activity Mapper"
TOP_ROW_HEIGHT = 200
BOTTOM_ROW_HEIGHT = 500
APP_URL = os.environ.get("APP_URL")
STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")

authorization_link = f"https://www.strava.com/oauth/authorize?client_id={STRAVA_CLIENT_ID}&response_type=code&redirect_uri={APP_URL}&approval_prompt=force&scope=read_all"


def get_token(authorization_code):
    response = requests.post(url="https://www.strava.com/oauth/token",
                             data={"client_id": STRAVA_CLIENT_ID,
                                   "client_secret": STRAVA_CLIENT_SECRET,
                                   "code": authorization_code,
                                   "grant_type": "authorization_code",
                                   "f": "json"})
    # if response.ok:
    #     return response.json().get("token")
    return response.json()


def main():
    params: dict = st.query_params.to_dict()
    code = params.get("code")
    if code:
        st.write("requesting token")
        # token = get_token(code)
        # st.write(f"{token=}")
    df = pd.DataFrame(columns=["app", "weekday", "time", "hour", "minutes", "name"])
    with st.spinner("Making visualizations..."):
        # sidebar
        with st.sidebar:
            st.write(f"{code=}")
            st.header("Menu")
            image_powered = bu.load_image("logos/api_logo_pwrdBy_strava_horiz_light.png")
            st.markdown(f'<img src="data:image/png;base64,{image_powered}" width="100%">',
                        unsafe_allow_html=True)
            image_connect = bu.load_image("logos/btn_strava_connectwith_orange@2x.png")
            st.markdown(f'<a href="{authorization_link}">'
                        f'<img src="data:image/png;base64,{image_connect}" width="100%">'
                        f'</a>',
                        unsafe_allow_html=True)

        # MAIN PAGE
        with st.container():
            st.subheader(TITLE)
            # top row
            st.plotly_chart(figure_or_data=bpc.timeline(df,
                                                        TOP_ROW_HEIGHT),
                               use_container_width=True)

        with st.container():
            # middle row
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
            st.write("")


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
