# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

All the plotly graph functions with the preprocessing and helper functions.

helper functions:
    _add_annotation
    _update_layout
    empty_figure

preprocessing and graph functions:
    timeline -> timeline_figure
days -> weekdays_figure
hours -> clock_figure
types -> sunburst_figure
locations -> process_data -> worldmap_figure

"""
# Standard library
import datetime as dt
import math
import typing
# Third party
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# Local imports
import backend


def _add_annotation(fig: go.Figure,
                    **kwargs: typing.Any) -> go.Figure:
    """
    A wrapper to add annotation to a figure to indicate it is empty.

    Parameters
    ----------
    fig : go.Figure
        The plotly figure.
    **kwargs : typing.Any
        Key word arguments.

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
                       showarrow=False,
                       **kwargs)
    return fig


def _add_annotation_color(fig: go.Figure,
                          x_pos: dt.date,
                          ax: int,
                          text: str) -> go.Figure:
    """


    Parameters
    ----------
    fig : go.Figure
        DESCRIPTION.
    x_pos : dt.date
        DESCRIPTION.
    ax : int
        DESCRIPTION.
    text : str
        DESCRIPTION.

    Returns
    -------
    fig : go.Figure
        DESCRIPTION.

    """
    fig.add_annotation(x=x_pos,
                       ax=ax,
                       y=5,
                       text=text,
                       font={"color": backend.COLOR_MAP.get("Strava"),
                             "family": "Arial",
                             "size": 12},
                       showarrow=True,
                       arrowcolor=backend.COLOR_MAP.get("Strava"))
    return fig


def _update_layout(fig: go.Figure,
                   **kwargs: typing.Any) -> go.Figure:
    """
    A wrapper to update the layout of a figure uniformly for all figures.

    Parameters
    ----------
    fig : go.Figure
        The plotly figure.
    **kwargs : typing.Any
        Key word arguments.

    Returns
    -------
    fig : go.Figure
        The plotly figure with updated layout.

    """
    xaxis = {"fixedrange": True}
    if "xaxis" in kwargs:
        xaxis.update(kwargs.get("xaxis"))
        kwargs.pop("xaxis")
    fig.update_layout(showlegend=False,
                      # set the margins of the graph to optimize visable area
                      margin={"l": backend.LEFT_RIGHT_MARGIN,
                              "r": backend.LEFT_RIGHT_MARGIN,
                              "t": backend.TOP_BOTTOM_MARGIN,
                              "b": backend.TOP_BOTTOM_MARGIN},
                      # prevent scrolling on the graphs
                      xaxis=xaxis,
                      yaxis={"fixedrange": True},
                      **kwargs)
    return fig


def empty_figure(title: str,
                 height: int = None,
                 **kwargs: typing.Any) -> go.Figure:
    """
    Create an empty figure with the title and a text label to show that no data
    is available to display.

    Parameters
    ----------
    title : str
        The title of the replaced figure.
    height : int, optional
        The desired height of the figure. The default is None.
    **kwargs : typing.Any
        Key word arguments.

    Returns
    -------
    figure : go.Figure
        An empty figure with the title of the original plot and an annotation.

    """
    figure = go.Figure()
    figure.update_layout(title=title,
                         height=height)
    figure = _add_annotation(figure,
                             **kwargs)
    return figure


def timeline_figure(aggregated_data: pd.DataFrame,
                    data: pd.DataFrame,
                    title: str,
                    height: int = None,
                    **kwargs: typing.Any) -> go.Figure:
    """
    Create an area plot to display the training intensity per calender week and
    overlay the data of the actual activities.

    Parameters
    ----------
    aggregated_data : pd.DataFrame
        The dataframe containing the grouped data for the plots.
    dataframe : pd.DataFrame
        The dataframe containing the data for the plots.
    title : str
        The title of the plot.
    height : int, optional
        The height of the plot. The default is None.
    **kwargs : typing.Any
        Key word arguments.

    Returns
    -------
    figure : go.Figure
        The plotly area figure with an overlayed scatter plot.

    """
    xaxis = kwargs.get("x")
    yaxis = kwargs.get("y")
    app = kwargs.get("group")
    figure = px.area(data_frame=aggregated_data,
                     x=xaxis,
                     y=yaxis,
                     line_group=app,
                     color=app,
                     hover_name=None,
                     hover_data={app: False,
                                 xaxis: False,
                                 yaxis: False
                                 },
                     custom_data=[app],
                     labels={xaxis: "Year"},  # change the label on the plot
                     color_discrete_map=backend.COLOR_MAP,
                     orientation="v",  # orient the chart
                     line_shape="spline",  # smoothes out the line
                     title=title,
                     template=backend.TEMPLATE,
                     height=height,
                     **kwargs.get("area", {})
                     )
    figure.update_traces(hovertemplate="Activity on %{customdata[0]}")
    figure.add_scatter(customdata=data.loc[:, ["name", "date"]].values,
                       hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}",
                       marker={"size": 3},
                       mode="markers",  # select drawing mode
                       name="",  # set trace name to empty
                       opacity=1,  # make points non-transparant
                       x=data[kwargs.get("scatter_x")],  # position the dots by week
                       y=data[kwargs.get("scatter_y")],
                       **kwargs.get("scatter", {})
                       )
    figure.add_vline((creation_date := kwargs.get("creation_date")),
                     line_width=1,
                     line_color=backend.COLOR_MAP.get("Strava"))
    figure.add_vline((today := dt.datetime.now().date()),
                     line_width=1,
                     line_color=backend.COLOR_MAP.get("Strava"))
    figure = _add_annotation_color(figure,
                                   creation_date,
                                   100,
                                   "Strava profile created")
    figure = _add_annotation_color(figure,
                                   today,
                                   -100,
                                   "Today")
    figure = _update_layout(figure,
                            xaxis={"range": [creation_date - dt.timedelta(days=2),
                                             today + dt.timedelta(days=2)]}
                            )
    return figure


def weekdays_figure(aggregated_data: pd.DataFrame,
                    title: str,
                    height: int = None,
                    **kwargs: typing.Any) -> go.Figure:
    """


    Parameters
    ----------
    aggregated_data : pd.DataFrame
        The dataframe containing the grouped data for the plots.
    title : str
        The title of the plot.
    height : int, optional
        The height of the plot. The default is None.
    **kwargs : typing.Any
        Key word arguments.

    Returns
    -------
    figure : go.Figure
        The plotly bar figure.

    """
    hover_data = [day for num, day in enumerate(["Monday",
                                                 "Tuesday",
                                                 "Wednesday",
                                                 "Thursday",
                                                 "Friday",
                                                 "Saturday",
                                                 "Sunday"])
                  if num in aggregated_data.weekday]
    figure = px.bar(data_frame=aggregated_data,
                    x="weekday",
                    y="percentage",
                    color="app",
                    color_discrete_map=backend.COLOR_MAP,
                    hover_data=[hover_data,
                                ],
                    text_auto=".0%",
                    title=title,
                    template=backend.TEMPLATE,
                    height=height,
                    **kwargs
                    )
    figure.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>%{y}")
    figure.update_layout(xaxis={"tickmode": "array",
                                "tickvals": list(range(7)),
                                # relabel the xaxis ticks
                                "ticktext":
                                    ["M", "T", "W", "T", "F", "S", "S"],
                                # fix that all labels are shown even if the column is empty
                                "range": [-.5, 6.5]
                                },
                         yaxis={"tickmode": "linear",
                                "tick0": 0,
                                "dtick": 0.05,
                                "tickformat": ".0%"}
                         )
    figure = _update_layout(figure)
    return figure


def clock_figure(preprocessed_data: pd.DataFrame,
                 title: str,
                 height: int = None,
                 **kwargs: typing.Any) -> go.Figure:
    """


    Parameters
    ----------
    preprocessed_data : pd.DataFrame
        The dataframe containing the grouped data for the plots.
    title : str
        The title of the plot.
    height : int, optional
        The height of the plot. The default is None.
    **kwargs : typing.Any
        Key word arguments.

    Returns
    -------
    figure : go.Figure
        The plotly polar scatter plot.

    """
    figure = px.scatter_polar(data_frame=preprocessed_data,
                              r="count",
                              theta="timestep",
                              color="app",
                              hover_name="name",
                              custom_data=["name", "time"],
                              color_discrete_map=backend.COLOR_MAP,
                              direction="clockwise",
                              start_angle=90,  # start at due north
                              title=title,
                              template=backend.TEMPLATE,
                              height=height,
                              **kwargs
                              )
    figure.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}")
    max_axis = 0 if preprocessed_data.empty else int(preprocessed_data["count"].max())
    figure = _update_layout(figure)
    figure.update_layout(polar={"radialaxis": {"tickvals":
                                               list(range(0, max_axis+1, 5))},
                                "angularaxis": {"tickvals":
                                                [backend.hr2ang(hr) for hr in range(24)],
                                                "ticktext":
                                                [str(24 if hr == 0 else hr) for hr in range(24)]}
                                }
                         )
    return figure


def sunburst_figure(aggregated_data: pd.DataFrame,
                    title: str,
                    height: int = None,
                    **kwargs: typing.Any) -> go.Figure:
    """


    Parameters
    ----------
    aggregated_data : pd.DataFrame
        The dataframe containing the grouped data for the plots.
    title : str
       The title of the plot.
    height : int, optional
        The height of the plot. The default is None.
    **kwargs : typing.Any
        Key word arguments.

    Returns
    -------
    figure : go.Figure
        The plotly sunburst figure.

    """
    figure = px.sunburst(data_frame=aggregated_data,
                         path=["type", "sport_type"],
                         values="counts",
                         color_discrete_sequence=backend.DISCRETE_COLOR,
                         title=title,
                         template=backend.TEMPLATE,
                         height=height,
                         **kwargs)
    figure.update_traces(hovertemplate="<b>%{label}</b><br>%{value}")
    figure = _update_layout(figure)
    return figure


def worldmap_figure(data: pd.DataFrame,
                    countries: pd.DataFrame,
                    geojson: dict,
                    title: str,
                    height: int = None,
                    **kwargs: typing.Any) -> go.Figure:
    """


    Parameters
    ----------
    data : pd.DataFrame
        The dataframe containing the data for the plots.
    countries: pd.DataFrame
        <>
    geojson: dict
        <>
    title : str
        The title of the plot.
    height : int, optional
        The height of the plot. The default is None.
    **kwargs : typing.Any
        Key word arguments.

    Returns
    -------
    figure : go.Figure
        The plotly line mapbox of the locations and routes overlayed with the scatter plot.

    """
    lats: list = kwargs.get("lat", [])
    lons: list = kwargs.get("lon", [])
    name: list = kwargs.get("name", [])
    # color the countries by (log of) the amount of activities
    figure = px.choropleth_mapbox(data_frame=countries,
                                  geojson=geojson,
                                  featureidkey="properties.ADMIN",
                                  locations=countries["country"],
                                  color="count",
                                  # remover hover label for choropleth plot
                                  hover_data={"country": False,
                                              "count": False},
                                  color_continuous_scale=px.colors.sequential.Oranges,
                                  range_color=[0, countries["count"].max()],
                                  opacity=.5,
                                  zoom=1,
                                  # center map on coordinates of activities
                                  center={"lat": data["lat"].mean(),
                                          "lon": data["lon"].mean()},
                                  mapbox_style="carto-darkmatter",
                                  title=title,
                                  height=height
                                  )
    # figure.add
    # add the routes of the activities
    figure.add_scattermapbox(below="",  # put trace above all others
                             lat=lats,
                             lon=lons,
                             marker={"size": 1,
                                     "color": backend.COLOR_MAP.get("Strava"),
                                     "symbol": "circle",
                                     },
                             mode="lines",
                             customdata=name
                             )
    figure.add_scattermapbox(below="",   # put trace above all others
                             lat=data["lat"],
                             lon=data["lon"],
                             marker={"size": 5,
                                     "color": backend.COLOR_MAP.get("Strava"),
                                     "symbol": "circle",
                                     },
                             mode="markers",
                             customdata=data["name"]
                             )
    figure.update_traces(hovertemplate="%{customdata}")
    figure = _update_layout(figure)
    figure.update_layout(coloraxis_showscale=False)
    return figure


def timeline(original: pd.DataFrame,
             plot_height: int,
             **kwargs: typing.Any) -> go.Figure:
    """
    Create an area plot to display the training intensity per calender week and
    overlay the data of the actual activities.

    Parameters
    ----------
    original : pd.DataFrame
        The entire dataframe.
    plot_height : int
        The height of the plot.
    **kwargs : typing.Any
        Key word arguments.

    Returns
    -------
    time_line: go.Figure
        DESCRIPTION.

    """
    # show empty figure if no data is provided
    plot_title = "Timeline"
    if original.empty:
        return empty_figure(plot_title,
                            plot_height)
    # prepare data
    summarize_name = "Times per week"
    name = "calender-week"
    dataframe = original.copy()
    dataframe["pos"] = 0
    last = None
    count = None
    for index, row in dataframe.loc[:].iterrows():
        week = row[name]
        if week != last:
            last = week
            count = 0
            continue
        count += 1
        dataframe.loc[index, "pos"] = count
    # rework the calender-week column to be the first day of the week
    # TODO: update use of .loc
    dataframe["cw"] = dataframe.loc[:, ["year", "week"]]\
        .apply(lambda row: f"{row[0]}-{row[1]}-1",
               axis=1)
    dataframe["cw"] = pd.to_datetime(dataframe["cw"],
                                     format="%Y-%W-%w")
    # summarize the amount of activities per week
    data = dataframe.groupby(["app", "year", "week"])["timestamp"]\
        .count().reset_index().rename({"timestamp": summarize_name},
                                      axis=1)
    # rework the calender-week column to be the first day of the week
    # TODO: update use of .loc
    data[name] = data.loc[:, ["year", "week"]].apply(
        lambda row: f"{row[0]}-{row[1]}-1", axis=1)
    # TODO: update use of pd.to_datetime
    data[name] = pd.to_datetime(data[name],
                                format="%Y-%W-%w")

    # make creation_
    creation_date: dt.date = dt.datetime.strptime(kwargs.get("creation"),
                                                  "%Y-%m-%dT%H:%M:%SZ").date()
    # create figure
    time_line = timeline_figure(data,
                                dataframe,
                                title=plot_title,
                                height=plot_height,
                                x=name,
                                y=summarize_name,
                                group="app",
                                creation_date=creation_date,
                                scatter_x="cw",
                                scatter_y="pos",
                                **kwargs)
    return time_line


def days(original: pd.DataFrame,
         plot_height: int,
         **kwargs: typing.Any) -> go.Figure:
    """


    Parameters
    ----------
    original : pd.DataFrame
        The entire dataframe.
    plot_height : int
        The height of the plot.
    **kwargs : typing.Any
        Key word arguments.

    Returns
    -------
    weekdays : go.Figure
        DESCRIPTION.

    """

    plot_title = "Weekdays"
    # prepare data
    data = original.sort_values("date").groupby(["app", "weekday"])["time"].count().reset_index()\
        .rename({"time": "counts"},
                axis=1)
    data["percentage"] = data["counts"] / original.shape[0]
    # create figure
    weekdays = weekdays_figure(data,
                               title=plot_title,
                               height=plot_height,
                               **kwargs)
    # show empty figure if no data is provided
    if original.empty:
        weekdays = _add_annotation(weekdays)
    return weekdays


def hours(original: pd.DataFrame,
          plot_height: int,
          **kwargs: typing.Any) -> go.Figure:
    """


    Parameters
    ----------
    original : pd.DataFrame
        The entire dataframe.
    plot_height : int
        The height of the plot.
    **kwargs : typing.Any
        Key word arguments.

    Returns
    -------
    clock : go.Figure
        DESCRIPTION.

    """
    plot_title = "Hours"
    # prepare data
    original["timestep"] = original["hour"]*60 + original["minutes"]//10
    original["timestep"] = original["timestep"].apply(backend.min2ang)
    original.sort_values(by="timestep",
                         ascending=True,
                         inplace=True)
    original["count"] = 1
    last = None
    count = None
    for index, row in original.loc[:].iterrows():
        step = row["timestep"]
        if step != last:
            last = step
            count = 1
            continue
        count += 1
        original.loc[index, "count"] = count
    # create figure
    clock = clock_figure(original,
                         title=plot_title,
                         height=plot_height,
                         **kwargs)
    # show empty figure if no data is provided
    if original.empty:
        clock = _add_annotation(clock)
    return clock


def types(original: pd.DataFrame,
          plot_height: int,
          **kwargs: typing.Any) -> go.Figure:
    """


    Parameters
    ----------
    original : pd.DataFrame
        The entire dataframe.
    plot_height : int
        The height of the plot.
    **kwargs : typing.Any
        Key word arguments.

    Returns
    -------
    types_plot : go.Figure
        DESCRIPTION.

    """
    plot_title = "Activity types"
    # show empty figure if no data is provided
    if original.empty:
        return empty_figure(plot_title,
                            plot_height)
    # prepare data
    data = original.copy()
    mapper = backend.load_category_mapper(backend.PATH_MAPPER)
    data["type"] = data["sport_type"].map(mapper)
    data["counts"] = 1
    # create figure
    types_plot = sunburst_figure(data,
                                 title=plot_title,
                                 height=plot_height,
                                 **kwargs)
    return types_plot


def process_data(data: pd.DataFrame,
                 **kwargs: typing.Any) -> dict[list]:
    """


    Parameters
    ----------
    data : pd.DataFrame
        The dataframe containing rows with a lat and a lon coordinate.
    **kwargs : typing.Any
        Key word arguments.

    Returns
    -------
    list: dict[list]
        A dictionary with the lists of values for the line mapbox.

    """
    _ = kwargs
    lats = []
    lons = []
    colors = []
    names = []
    dates = []
    times = []
    for _, row in data.iterrows():
        segment_length = len(coords := row["coords"])+1
        lat, lon = zip(*coords)  # unpack a list of tuples to two lists
        lat = [row["lat"]]+list(lat)
        lon = [row["lon"]]+list(lon)
        lats.extend(lat)
        lons.extend(lon)

        colors.extend([row["app"]]*segment_length)
        names.extend([row["name"]]*segment_length)
        dates.extend([row["date"]]*segment_length)
        times.extend([row["time"]]*segment_length)
        # make a seperation in the lists

        lats.append(None)
        lons.append(None)
        colors.append(row["app"])
        names.append(None)
        dates.append(None)
        times.append(None)
    lists = {"lat": lats,
             "lon": lons,
             "color": colors,
             "name": names,
             "date": dates,
             "time": times}
    return lists


def locations(original: pd.DataFrame,
              plot_height: int,
              **kwargs: typing.Any) -> go.Figure:
    """


    Parameters
    ----------
    original : pd.DataFrame
        The entire dataframe.
    plot_height : int
        The height of the plot.
    **kwargs : typing.Any
        Key word arguments.

    Returns
    -------
    worldmap : go.Figure
        The world map with the start and locations, and routes.

    """

    # show empty figure if no data is provided
    plot_title = "Locations"
    # prepare data
    data = original.copy()
    countries_count = pd.DataFrame(columns=["country", "count"])
    data = data.loc[(~original["lat"].isna()) &
                    (~original["lon"].isna()),
                    :]
    if not data.empty:
        countries_count = data.country.value_counts().reset_index()
        # get the colors closer together by taking the log of the value
        countries_count["count"] = countries_count["count"].apply(math.log) + 2
    geojson_file = backend.load_geojson(backend.PATH_GEOJSON)
    # create figure
    worldmap = worldmap_figure(data,
                               countries_count,
                               geojson_file,
                               title=plot_title,
                               height=plot_height,
                               **process_data(data),
                               zoom=1,
                               **kwargs)
    if data.empty:
        worldmap = _add_annotation(worldmap)
    return worldmap


if __name__ == "__main__":
    pass
