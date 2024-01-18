# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""

import streamlit as st

TITLE = "Activity Mapper"

def main():
    with st.spinner("Making visualizations."):
        # SIDEBAR
        with st.sidebar:
            st.header("Menu")

        # MAIN PAGE
        with st.container():
            st.header(TITLE)



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
