# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

<>
"""
# Standard library
import datetime as dt
import os
# Third party
import pandas as pd
import streamlit as st
# Local imports
import backend


def refresh_access_token(refresh_token):
    response = backend.post_request(backend.TOKEN_LINK,
                                    data={"client_id": backend.STRAVA_CLIENT_ID,
                                          "client_secret": backend.STRAVA_CLIENT_SECRET,
                                          "grant_type": "refresh_token",
                                          "refresh_token": refresh_token}
                                    )
    refresh_token = response.get("refresh_token")
    access_token = response.get("access_token")
    athlete = backend.get_request("https://www.strava.com/api/v3/athlete",
                                  headers = {"Authorization": f"Bearer {access_token}"})
    athlete_name = " ".join((athlete.get("firstname", ""),
                             athlete.get("lastname", "")
                             )
                            )
    created_at = athlete.get("created_at", "Not found")
    return access_token, refresh_token, athlete_name, created_at


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
    # TODO: make a get refresg token function
    results = backend.get_access_token(code)
    st.session_state["access_token"]: str = results[0]
    st.session_state["refresh_token"]: str = results[1]
    st.session_state["athlete_name"]: str = results[2]
    st.session_state["creation"]: str = results[3]
    # RETREIVING THE DATA
    progress_bar.progress(33, "Retreiving data...")
    data = backend.thread_get_and_parse(st.session_state["access_token"])
    # if an error occur stop the function
    if data.iloc[0].name == "401":
        if "refresh_token" in st.session_state:
            refresh_access_token(st.session_state.get("refresh_token"))
        error_message = st.error(backend.ERROR_MESSAGE)
        return
    # PARSING THE DATA
    progress_bar.progress(67, "Parsing data...")
    # dataframe = backend.parse(data)
    st.session_state["dataframe"] = data#frame
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
    # DEBUG
    with st.expander("DEBUG"):
        st.write(refresh_access_token(st.session_state.get("refresh_token")))
        st.dataframe(st.session_state.get("dataframe"))
    welcome_text = "Welcome" if not (n:=st.session_state.get('athlete_name')) else f"Welcome, {n}"
    df = st.session_state.get("dataframe",
                              pd.DataFrame(columns=backend.STRAVA_COLS))
    with st.spinner("Making visualizations..."):
        # sidebar
        with st.sidebar:
            image_powered = backend.load_image("logos/api_logo_pwrdBy_strava_horiz_light.png")
            st.markdown(f'<img src="data:image/png;base64,{image_powered}" width="100%">',
                        unsafe_allow_html=True)
            st.header("Menu")
            if not st.session_state.get("loaded"):
                image_connect = backend.load_image("logos/btn_strava_connectwith_orange@2x.png")
                st.markdown(f'<a href="{backend.authorization_link}">'
                            f'<img src="data:image/png;base64,{image_connect}" width="100%">'
                            f'</a>',
                            unsafe_allow_html=True)
            else:
                st.error("connected")
            st.divider()
            st.markdown(backend.EXPLANATION)
            if st.button("Show with demo data"):
                test_data = backend.parse(backend.load_test_data())
                st.session_state["dataframe"] = test_data
                wrap_up()

        # MAIN PAGE
        with st.container():
            st.markdown(f"## {backend.TITLE}: {welcome_text}")
            # top row
            st.plotly_chart(figure_or_data=backend.timeline(df,
                                                        backend.TOP_ROW_HEIGHT,
                                                        creation=st.session_state.get("creation",
                                                                                      "" if df.empty else dt.datetime.strftime(df.date.min(),            "%Y-%m-%dT%H:%M:%SZ"))

                                                        ),
                               use_container_width=True,
                               config=backend.CONFIG)

        with st.container():
            # middle row
            cols = st.columns(spec=[6,6],
                              gap="small")
            cols[0].plotly_chart(figure_or_data=backend.days(df,
                                                         backend.BOTTOM_ROW_HEIGHT//3-50),
                                  use_container_width=True,
                                  config=backend.CONFIG)
            cols[1].plotly_chart(figure_or_data=backend.locations(df,
                                                              backend.BOTTOM_ROW_HEIGHT),
                                 use_container_width=True,
                                 config=backend.CONFIG2)
            subcols = cols[0].columns(spec=[3,3], gap="small")
            subcols[0].plotly_chart(figure_or_data=backend.types(df,
                                                             backend.BOTTOM_ROW_HEIGHT//1.5),
                                  use_container_width=True,
                                  config=backend.CONFIG)
            subcols[1].plotly_chart(figure_or_data=backend.hours(df,
                                                             backend.BOTTOM_ROW_HEIGHT//1.5),
                                  use_container_width=True,
                                  config=backend.CONFIG)
            # SLIDER
        data=st.session_state.get("dataframe",
                                               pd.DataFrame(columns=backend.DISPLAY_COLS)
                                               ).loc[:, backend.DISPLAY_COLS]
        data["id"] = data["id"].apply(lambda id_:f"https://www.strava.com/activities/{id_}")
        with st.expander(f"See your {data.shape[0]} unique events", expanded = False):
            st.dataframe(data,
                         use_container_width=True,
                         hide_index=True,
                         column_order=backend.DISPLAY_COLS,
                         column_config={"id":
                                        st.column_config.LinkColumn(label="view on Strava",
                                                                    help=\
                                        "See this activity on the Strava website")
                                        }
                         )
        st.caption(backend.CAPTION)


if __name__ == "__main__":
    # set the initial state of the sidebar
    if "sidebar_state" not in st.session_state:
        st.session_state["sidebar_state"] = "expanded"
    st.set_page_config(page_title=backend.TITLE,
                       page_icon=":world_map:",
                       layout="wide",
                       initial_sidebar_state=st.session_state.get("sidebar_state")
                       )
    main()
