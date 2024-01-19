# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""
# Standard library

# Third party
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# Local imports

TEMPLATE = None

def empty_figure(title: str,
                 height: int = None) -> go.Figure:
    figure = go.Figure()
    figure.update_layout(title=title,
                         height=height)
    figure.add_annotation(x=2,
                          y=2,
                          text="No Data to Display",
                          font={"family": "sans serif",
                                "size": 25},
                          showarrow=False)
    return figure


def timeline_figure(data: pd.DataFrame,
                    title:str,
                    height: int = None):
    figure = px.area(data_frame=data,
                     title=title,
                     template=TEMPLATE,
                     height=height
                     )
    return figure


def weekdays_figure(data: pd.DataFrame,
                    title:str,
                    height: int = None):
    figure = px.bar(data_frame=data,
                    title=title,
                    template=TEMPLATE,
                    height=height
                    )
    return figure


def clock_figure(data: pd.DataFrame,
                 title:str,
                 height: int = None):
    figure = px.scatter_polar(data_frame=data,
                              title=title,
                              template=TEMPLATE,
                              height=height
                              )
    return figure


def pie_figure(data: pd.DataFrame,
               title:str,
               height: int = None):
    figure = px.pie(data_frame=data,
                    title=title,
                    template=TEMPLATE,
                    height=height
                    )
    return figure


def worldmap_figure(data: pd.DataFrame,
                    title:str,
                    height: int = None):
    figure = px.line_mapbox(data_frame=data,
                            title=title,
                            template=TEMPLATE,
                            height=height
                            )
    return figure


def timeline(dataframe: pd.DataFrame,
             plot_height: int):

    # show empty figure if no data is provided
    plot_title = "Timeline"
    if dataframe.empty:
        return empty_figure(plot_title,
                            plot_height)
    # prepare data

    # create figure
    time_line = timeline_figure(dataframe,
                                title=plot_title,
                                height=plot_height)
    return time_line



def days(dataframe: pd.DataFrame,
         plot_height: int):

    # show empty figure if no data is provided
    plot_title = "Weekdays"
    if dataframe.empty:
        return empty_figure(plot_title,
                            plot_height)
    # prepare data

    # create figure
    weekdays = weekdays_figure(dataframe,
                               title=plot_title,
                               height=plot_height)
    return weekdays


def hours(dataframe: pd.DataFrame,
          plot_height: int):

    # show empty figure if no data is provided
    plot_title = "Hours"
    if dataframe.empty:
        return empty_figure(plot_title,
                            plot_height)
    # prepare data

    # create figure
    clock = clock_figure(dataframe,
                         title=plot_title,
                         height=plot_height)
    return clock


def types(dataframe: pd.DataFrame,
          plot_height: int):

    # show empty figure if no data is provided
    plot_title = "Activity types"
    if dataframe.empty:
        return empty_figure(plot_title,
                            plot_height)
    # prepare data

    # create figure
    pie = pie_figure(dataframe,
                     title=plot_title,
                     height=plot_height)
    return pie


def locations(dataframe: pd.DataFrame,
              plot_height: int):

    # show empty figure if no data is provided
    plot_title = "Locations"
    if dataframe.empty:
        return empty_figure(plot_title,
                            plot_height)
    # prepare data

    # create figure
    worldmap = worldmap_figure(dataframe,
                               title=plot_title,
                               height=plot_height)
    return worldmap


if __name__=="__main__":
    pass
