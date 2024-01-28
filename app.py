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
STRAVA_COLS = ["app", "weekday", "time", "hour", "minutes", "name"]
DISPLAY_COLS = ["name", "date", "type", "sport_type", "view on Strava"]
authorization_link = "https://www.strava.com/oauth/authorize"+\
    f"?client_id={STRAVA_CLIENT_ID}&response_type=code&"+\
    f"redirect_uri={APP_URL}&approval_prompt=force&"+\
    "scope=activity:read,activity:read_all"
CONFIG = {"displaylogo": False,
          "displayModeBar": False,}
CONFIG2 = {"displaylogo": False,
           "modeBarButtonsToRemove": ["pan2d",
                                      "lasso2d",
                                      "select2d",
                                      "toImage",
                                      "zoom2d",
                                      "autoscale"]}


def connect_strava(code):
    error_message = st.empty()
    # RETREIVING THE ACCESS TOKEN
    progress_bar = st.progress(0, "Getting access token")
    results = bsp.get_access_token(code)
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
    # FINALIZE THE PROCESS
    progress_bar.progress(100, "Done")
    # dataframe = st.session_state.get("dataframe")
    progress_bar.empty()
    wrap_up()
    return

def wrap_up():
    st.session_state["sidebar_state"] = "collapsed"
    # raise flag that data has been loaded
    st.session_state["loaded"] = True
    # rerun the page to have header and sidebar be updated
    st.rerun()


def main():
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
            if not st.session_state.get("athlete_name"):
                image_connect = bu.load_image("logos/btn_strava_connectwith_orange@2x.png")
                st.markdown(f'<a href="{authorization_link}">'
                            f'<img src="data:image/png;base64,{image_connect}" width="100%">'
                            f'</a>',
                            unsafe_allow_html=True)
            else:
                st.error("connected")
            st.divider()
            st.markdown(body=open("intro.txt").read())
            if st.button("Show with demo data"):
                st.session_state["dataframe"] = bsp.parse(bt.load_test_data())
                wrap_up()

        # MAIN PAGE
        with st.container():
            st.header("TITLE")
            # st.subheader(": ".join([TITLE, welcome_text]))
            st.markdown("""# TITLE
                        ## title""")
            # top row
            st.plotly_chart(figure_or_data=bpc.timeline(df,
                                                        TOP_ROW_HEIGHT),
                               use_container_width=True,
                               config=CONFIG)

        with st.container():
            # middle row
            cols = st.columns(spec=[6,6],
                              gap="small")
            cols[0].plotly_chart(figure_or_data=bpc.days(df,
                                                         BOTTOM_ROW_HEIGHT/2),
                                  use_container_width=True,
                                  config=CONFIG)
            cols[1].plotly_chart(figure_or_data=bpc.locations(df,
                                                              BOTTOM_ROW_HEIGHT),
                                 use_container_width=True,
                                 config=CONFIG2)
            subcols = cols[0].columns(spec=[3,3], gap="small")
            subcols[0].plotly_chart(figure_or_data=bpc.types(df,
                                                             BOTTOM_ROW_HEIGHT/2),
                                  use_container_width=True,
                                  config=CONFIG)
            subcols[1].plotly_chart(figure_or_data=bpc.hours(df,
                                                             BOTTOM_ROW_HEIGHT/2),
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
