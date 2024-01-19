# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""
# Standard library

# Third party
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def empty_figure(title, height):
    figure = go.Figure()
    figure.update_layout(title=title,
                         height=height)
    return figure


def timeline(dataframe, height):

    # show empty figure if no data is provided
    plot_title = "Timeline"
    if dataframe.empty:
        return empty_figure(plot_title, height)


def days(dataframe, height):

    # show empty figure if no data is provided
    plot_title = "Weekdays"
    if dataframe.empty:
        return empty_figure(plot_title, height)


def hours(dataframe, height):

    # show empty figure if no data is provided
    plot_title = "Hours"
    if dataframe.empty:
        return empty_figure(plot_title, height)


def activity_types(dataframe, height):

    # show empty figure if no data is provided
    plot_title = "Activity types"
    if dataframe.empty:
        return empty_figure(plot_title, height)

def locations(dataframe, height):

    # show empty figure if no data is provided
    plot_title = "Locations"
    if dataframe.empty:
        return empty_figure(plot_title, height)
