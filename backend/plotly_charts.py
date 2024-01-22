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


def _add_annotation(fig: go.Figure) -> go.Figure:
    """


    Parameters
    ----------
    fig : go.Figure
        DESCRIPTION.

    Returns
    -------
    fig : go.Figure
        The plotly figure with annotation.

    """
    fig.add_annotation(x=2,
                       y=2,
                       text="No Data to Display",
                       font={"family": "sans serif",
                             "size": 25},
                       showarrow=False)
    return fig


def empty_figure(title: str,
                 height: int = None) -> go.Figure:
    """
    Create an empty figure with the title and a text label to show that no data is
    available to display.

    Parameters
    ----------
    title : str
        The title of the replaced figure.
    height : int, optional
        The desired height of the figure. The default is None.

    Returns
    -------
    figure : TYPE
        An empty figure with the title of the original plot and an annotation.

    """
    figure = go.Figure()
    figure.update_layout(title=title,
                         height=height)
    figure = _add_annotation(figure)
    return figure


def timeline_figure(data: pd.DataFrame,
                    dataframe,
                    title:str,
                    height: int = None,
                    **kwargs):
    figure = px.area(data_frame=data,
                     x=kwargs.get("x"),
                     y=kwargs.get("y"),
                     title=title,
                     template=TEMPLATE,
                     height=height
                     )
    figure.update_traces()
    figure.update_layout(showlegend=False)
    figure.add_scatter(customdata=dataframe.loc[:,["name","date"]].values,
                       hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}",
                       marker={"size": 3},
                       mode="markers", # select drawing mode
                       name="", # set trace name to empty
                       opacity=1,
                       x=dataframe["cw"], # position the dots by week
                       y=dataframe["pos"],)
    return figure


def weekdays_figure(data: pd.DataFrame,
                    title:str,
                    height: int = None):
    figure = px.bar(data_frame=data,
                    x="weekday",
                    y="percentage",
                    title=title,
                    template=TEMPLATE,
                    height=height
                    )
    figure.update_traces()
    figure.update_layout(showlegend=False)
    return figure


def clock_figure(data: pd.DataFrame,
                 title:str,
                 height: int = None):
    figure = px.scatter_polar(data_frame=data,
                              title=title,
                              template=TEMPLATE,
                              height=height
                              )
    figure.update_traces()
    figure.update_layout(showlegend=False)
    return figure


def pie_figure(data: pd.DataFrame,
               title:str,
               height: int = None):
    figure = px.pie(data_frame=data,
                    title=title,
                    template=TEMPLATE,
                    height=height
                    )
    figure.update_traces()
    figure.update_layout(showlegend=False)
    return figure


def worldmap_figure(data: pd.DataFrame,
                    title:str,
                    height: int = None):
    figure = px.line_mapbox(#data_frame=data,
                            lat=[],
                            lon=[],
                            title=title,
                            template=TEMPLATE,
                            height=height
                            )
    figure.update_traces()
    figure.update_layout(showlegend=False)
    return figure


def timeline(dataframe: pd.DataFrame,
             plot_height: int):

    # show empty figure if no data is provided
    plot_title = "Timeline"
    if dataframe.empty:
        return empty_figure(plot_title,
                            plot_height)
    # prepare data
    summarize_name = "times per week"
    dataframe["pos"] = 0
    last = None
    count = None
    for index, row in dataframe.loc[:].iterrows():
        week = row["calender-week"]
        if week != last:
            last = week
            count = 0
            continue
        count += 1
        dataframe.loc[index,"pos"] = count
    # rework the calender-week column to be the first day of the week
    dataframe["cw"] = dataframe.loc[:,["year","week"]]\
        .apply(lambda row: f"{row[0]}-{row[1]}-1",
               axis=1)
    dataframe["cw"] = pd.to_datetime(dataframe["cw"],
                                     format="%Y-%W-%w")
    # summarize the amount of activities per week
    data = dataframe.groupby(["app", "year", "week"])["timestamp"]\
        .count().reset_index().rename({"timestamp": summarize_name}, axis=1)
    # rework the calender-week column to be the first day of the week
    data["calender-week"] = data.loc[:,["year","week"]].apply(lambda row: f"{row[0]}-{row[1]}-1",
                                                              axis=1)
    # TODO: update use of pd.to_datetime
    data["calender-week"] = pd.to_datetime(data["calender-week"],
                                            format="%Y-%W-%w")
    print(data)
    # create figure
    time_line = timeline_figure(data,
                                dataframe,
                                title=plot_title,
                                height=plot_height,
                                x="calender-week",
                                y=summarize_name)
    return time_line


def types(dataframe: pd.DataFrame,
          plot_height: int):
    plot_title = "Activity types"
    # show empty figure if no data is provided
    if dataframe.empty:
        return empty_figure(plot_title,
                            plot_height)
    # prepare data

    # create figure
    pie = pie_figure(dataframe,
                     title=plot_title,
                     height=plot_height)
    return pie


def hours(dataframe: pd.DataFrame,
          plot_height: int):
    plot_title = "Hours"
    # prepare data

    # create figure
    clock = clock_figure(dataframe,
                         title=plot_title,
                         height=plot_height)
    # show empty figure if no data is provided
    if dataframe.empty:
        # TODO: add annotation
        pass
    return clock


def days(dataframe: pd.DataFrame,
         plot_height: int):


    plot_title = "Weekdays"
    # prepare data
    data = dataframe.groupby(["app","weekday"])["time"]\
            .count()\
            .reset_index()\
            .rename({"time": "counts"},
                    axis=1)
    data["percentage"] = data["counts"] / dataframe.shape[0]
    # create figure
    weekdays = weekdays_figure(data,
                               title=plot_title,
                               height=plot_height)
    # show empty figure if no data is provided
    if dataframe.empty:
        weekdays = _add_annotation(weekdays)
    return weekdays


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
