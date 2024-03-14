# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

<>
"""
# Standard library
import datetime as dt
# Third party
import pandas as pd
import streamlit as st
# Local imports
import backend


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
    with st.status(label="Downloading data...",
                   expanded=True,
                   state="running") as status:
        error_message = st.empty()
        # check if a sufficient scope was provided
        status.write("Checking scope")
        if st.session_state.get("scope") == "read":
            error_message = st.error(backend.ERROR_MESSAGE1)
            status.update(label="Insufficient scope",
                          expanded=True,
                          state="error")
            return
        # RETREIVING THE ACCESS TOKEN
        status.write("Getting access token")
        results = backend.get_access(code)
        st.session_state["access_token"]: str = results[0]
        st.session_state["refresh_token"]: str = results[1]
        st.session_state["athlete_name"]: str = results[2]
        st.session_state["creation"]: str = results[3]
        # check if an access token was returned
        status.write("Checking if token was returned")
        if st.session_state.get("access_token") is None:
            backend.refresh_access(st.session_state.get("refresh_token"))
            error_message = st.error(backend.ERROR_MESSAGE2)
            status.update(label="Unauthorized access",
                          expanded=True,
                          state="error")
            return
        # RETREIVING AND PARSING THE DATA
        status.write("Retrieving and parsing data")
        data = backend.thread_get_and_parse(
            st.session_state.get("access_token")
                                            )
        # FINALIZE THE PROCESS
        status.write("Store data")
        st.session_state["dataframe"]: pd.DataFrame = data
        # signal that data has been loaded
        st.session_state["loaded"]: bool = True
        wrap_up()
        status.update(label="Done!",
                      expanded=False,
                      state="complete")
    return


def wrap_up():
    """
    <>

    Returns
    -------
    None.

    """
    # set the sidebar to collapse after the rerun
    st.session_state["sidebar_state"]: str = "collapsed"
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
    st.session_state["scope"] = params.get("scope")
    if code and not st.session_state.get("loaded", False):
        connect_strava(code)
    welcome_text = "Welcome"\
        if not (n := st.session_state.get('athlete_name'))\
        else f"Welcome, {n}"
    df = st.session_state.get("dataframe",
                              pd.DataFrame(columns=backend.STRAVA_COLS)
                              ).loc[:, backend.STRAVA_COLS]
    creation = st.session_state.get("creation",
                                    "" if df.empty
                                    else dt.datetime.strftime(
                                        df.date.min(),
                                        backend.DT_FORMAT
                                                              )
                                    )
    figures = backend.thread_create_figures(df, creation)
    with st.spinner("Making visualizations..."):
        # sidebar
        with st.sidebar:
            image_powered = backend.load_image(backend.PATH_LOGO)
            st.markdown(f"""
            <img src='data:image/png;base64,{image_powered}' width='100%'>
                        """,
                        unsafe_allow_html=True
                        )
            st.header("Menu")
            if not st.session_state.get("loaded"):
                image_connect = backend.load_image(backend.PATH_CONNECT)
                st.markdown(f"""
            <a href="{backend.authorization_link}">
            <img src='data:image/png;base64,{image_connect}' width='100%'>
            </a>
                    """,
                            unsafe_allow_html=True
                            )
            else:
                st.error("connected")
            st.divider()
            st.markdown(backend.EXPLANATION)
            if st.button("Show with demo data"):
                test_data = backend.parse(backend.load_test_data())
                st.session_state["dataframe"] = test_data
                st.session_state["creation"] = dt.datetime.strftime(
                                                test_data.date.min(),
                                                backend.DT_FORMAT
                                                                    )
                wrap_up()

        # MAIN PAGE
        with st.container():
            st.markdown(f"## {backend.TITLE}: {welcome_text}")
            # top row
            st.plotly_chart(figure_or_data=figures[0],
                            use_container_width=True,
                            config=backend.CONFIG)

        with st.container():
            # middle row
            cols = st.columns(spec=[6, 6],
                              gap="small")
            cols[0].plotly_chart(figure_or_data=figures[1],
                                 use_container_width=True,
                                 config=backend.CONFIG)
            cols[1].plotly_chart(figure_or_data=figures[2],
                                 use_container_width=True,
                                 config=backend.CONFIG2)
            subcols = cols[0].columns(spec=[3, 3], gap="small")
            subcols[0].plotly_chart(figure_or_data=figures[3],
                                    use_container_width=True,
                                    config=backend.CONFIG)
            subcols[1].plotly_chart(figure_or_data=figures[4],
                                    use_container_width=True,
                                    config=backend.CONFIG)
            # SLIDER
        data = st.session_state.get("dataframe",
                                    pd.DataFrame(columns=backend.DISPLAY_COLS)
                                    ).loc[:, backend.DISPLAY_COLS]
        data["id"] = data["id"].apply(
            lambda id_: f"{backend.ACTIVITIES_URL}{id_}"
                                      )
        with st.expander(f"See your {data.shape[0]} unique events",
                         expanded=False):
            st.dataframe(data,
                         use_container_width=True,
                         hide_index=True,
                         column_order=backend.DISPLAY_COLS,
                         column_config={"id":
                                        st.column_config.LinkColumn(
                                            label="view on Strava",
                                            help=backend.HELP_TEXT
                                                                    )
                                        }
                         )
        st.caption(backend.CAPTION)


if __name__ == "__main__":
    # set the initial state of the sidebar
    if "sidebar_state" not in st.session_state:
        st.session_state["sidebar_state"] = "expanded"
    st.set_page_config(
        page_title=backend.TITLE,
        page_icon=":world_map:",
        layout="wide",
        initial_sidebar_state=st.session_state.get("sidebar_state")
                       )
    main()
