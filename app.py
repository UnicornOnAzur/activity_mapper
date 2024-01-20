# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""
# Standard library

# Third party
import streamlit as st
# Local imports
import backend.plotly_charts as bpc
import backend.strava_parser as bsp

TITLE = "Activity Mapper"
def test():
    import json
    with open("api_test.txt", "r") as f:
        data = json.load(f)
    return bsp.parse(data)
df = test()
st.write(type(df), df)

def main():
    with st.spinner("Making visualizations..."):
        # sidebar
        with st.sidebar:
            st.header("Menu")

    # MAIN PAGE
    with st.container():
        st.header(TITLE)
        # top row
        left, right = st.columns(spec=[6,6],
                                 gap="small")
        left.plotly_chart(figure_or_data=bpc.timeline(df,400),
                          use_container_width=True)
        right.plotly_chart(figure_or_data=bpc.locations(df,500),
                           use_container_width=True)
        # middel row
    # with st.container():
        cols = left.columns([2,1,1])
        cols[0].plotly_chart(figure_or_data=bpc.days(df,200),
                             use_container_width=True)
        cols[1].plotly_chart(figure_or_data=bpc.hours(df,200),
                             use_container_width=True)
        cols[2].plotly_chart(figure_or_data=bpc.types(df,200),
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
