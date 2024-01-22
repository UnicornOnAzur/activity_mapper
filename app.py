# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""
# Standard library

# Third party
import pandas as pd
import streamlit as st
# Local imports
import backend.plotly_charts as bpc
import backend.strava_parser as bsp

TITLE = "Activity Mapper"
TOP_ROW_HEIGHT = 200
BOTTOM_ROW_HEIGHT = 500

def test():
    import json
    with open("api_test.txt", "r") as f:
        data = json.load(f)
    return bsp.parse(data)

def main():
    df = pd.DataFrame(columns=["app", "weekday", "time"])
    with st.spinner("Making visualizations..."):
        # sidebar
        with st.sidebar:
            st.header("Menu")
            k = st.button("load")
            if k:
                df=test()

    # MAIN PAGE
    with st.container():
        st.header(TITLE)
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
