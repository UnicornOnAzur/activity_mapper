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
import backend.utils as bu

COLOR_MAP = {"Strava": "#FC4C02", # the color of the Strava app
             }
DISCRETE_COLOR = px.colors.sequential.Oranges_r
TEMPLATE = "plotly_dark"#None
LEFT_RIGHT_MARGIN = 20
TOP_BOTTOM_MARGIN = 25

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


def _update_layout(fig: go.Figure) -> go.Figure:
    """


    Parameters
    ----------
    fig : go.Figure
        DESCRIPTION.

    Returns
    -------
    fig : go.Figure
        DESCRIPTION.

    """
    fig.update_layout(showlegend=False,
                      margin={"l": LEFT_RIGHT_MARGIN,
                              "r": LEFT_RIGHT_MARGIN,
                              "t": TOP_BOTTOM_MARGIN,
                              "b": TOP_BOTTOM_MARGIN})
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


def timeline_figure(aggregated_data: pd.DataFrame,
                    dataframe: pd.DataFrame,
                    title:str,
                    height: int = None,
                    **kwargs):
    xaxis = kwargs.get("x")
    yaxis = kwargs.get("y")
    figure = px.area(data_frame=aggregated_data,
                     x=xaxis,
                     y=yaxis,
                     line_group="app",
                     color="app",
                     hover_name=None,
                     hover_data={"app": False,
                                 xaxis: False,
                                 yaxis: False
                                 },
                     custom_data=["app"],
                     color_discrete_map=COLOR_MAP,
                     orientation="v", # orient the chart
                     line_shape="spline", # smoothes out the line
                     title=title,
                     template=TEMPLATE,
                     height=height
                     )
    figure.update_traces(hovertemplate="Activity on %{customdata[0]}")
    figure.add_scatter(customdata=dataframe.loc[:,["name","date"]].values,
                       hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}",
                       marker={"size": 3},
                       mode="markers", # select drawing mode
                       name="", # set trace name to empty
                       opacity=1,
                       x=dataframe["cw"], # position the dots by week
                       y=dataframe["pos"],)
    figure = _update_layout(figure)
    return figure


def weekdays_figure(aggregated_data: pd.DataFrame,
                    title:str,
                    height: int = None):
    hover_data = [day for num, day in enumerate(["Monday",
                                             "Tuesday",
                                             "Wednesday",
                                             "Thursday",
                                             "Friday",
                                             "Saturday",
                                             "Sunday"]) if num in aggregated_data.weekday]
    figure = px.bar(data_frame=aggregated_data,
                    x="weekday",
                    y="percentage",
                    color="app",
                    color_discrete_map=COLOR_MAP,
                    hover_data=[hover_data,
                                ],
                    text_auto=".0%",
                    title=title,
                    template=TEMPLATE,
                    height=height
                    )
    figure.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>%{y}"
                         )
    figure.update_layout(xaxis = {"tickmode":"array",
                                  "tickvals": list(range(7)),
                                  # relabel the xaxis ticks
                                  "ticktext": ["M","T","W","T","F","S","S"],
                                  # fix that all labels are shown even if the column is empty
                                  "range":[-.5,6.5]
                                  },
                         yaxis = {"tickmode": "linear",
                                  "tick0": 0,
                                  "dtick": 0.05,
                                  "tickformat": ".0%"}
                         )
    figure = _update_layout(figure)
    return figure


def clock_figure(aggregated_data: pd.DataFrame,
                 title:str,
                 height: int = None):
    figure = px.scatter_polar(data_frame=aggregated_data,
                              r="count",
                              theta="timestep",
                              color="app",
                              hover_name="name",
                              custom_data=["name","time"],
                              color_discrete_map=COLOR_MAP,
                              direction="clockwise",
                              start_angle=90, #start at due north
                              title=title,
                              template=TEMPLATE,
                              height=height
                              )
    figure.update_traces()
    max_axis = 0 if aggregated_data.empty else int(aggregated_data["count"].max())
    figure = _update_layout(figure)
    figure.update_layout(polar={"radialaxis": {"tickvals":
                                               list(range(0, max_axis+1, 5))},
                                "angularaxis": {"tickvals":
                                                [bu.hr2ang(hr) for hr in range(24)],
                                                "ticktext":
                                                [str(24 if hr==0 else hr) for hr in range(24)]}
                                }
                         )
    return figure


def pie_figure(aggregated_data: pd.DataFrame,
               title:str,
               height: int = None):
    figure = px.pie(data_frame=aggregated_data,
                    names="sport_type",
                    values="counts",
                    color="sport_type",
                    color_discrete_sequence=DISCRETE_COLOR,
                    title=title,
                    template=TEMPLATE,
                    height=height
                    )
    figure.update_traces(textposition='inside', # set the percentage inside the chart
                         # show the category and the amount in the chart
                         textinfo="label+percent",
                         hovertemplate="<b>%{label}</b><br>%{value}"
                         )
    figure = _update_layout(figure)
    return figure


def worldmap_figure(data: pd.DataFrame,
                    title:str,
                    height: int = None,
                    **kwargs):
    lats = kwargs.get("lat", [])
    lons = kwargs.get("lon", [])
    colors = kwargs.get("color", [])
    names = kwargs.get("name", [])
    dates = kwargs.get("date", [])
    times = kwargs.get("time", [])
    zoom = kwargs.get("zoom", 0)
    figure = px.line_mapbox(data_frame=data,
                            lat=lats,
                            lon=lons,
                            color=colors,
                            hover_name=names,
                            custom_data=[names, dates, times],
                            color_discrete_map=COLOR_MAP,
                            zoom=zoom,
                            center={"lat": data.lat.median(),
                                    "lon": data.lon.median()
                                    },
                            mapbox_style="carto-darkmatter",
                            title=title,
                            template=TEMPLATE,
                            height=height
                            )
    figure.update_traces(hovertemplate="<br>".join(["<b>%{customdata[0]}</b>",
                                                    "%{customdata[1]}",
                                                    "%{customdata[2]}",
                                                    "(%{lat},%{lon})",
                                                    ],
                                                    ),
                          )
    figure = _update_layout(figure)
    # for app in (groups:=data.groupby("app").groups):
    #     app_data = data.loc[groups[app].values]
    #     figure.add_scattermapbox(below="traces",
    #                              customdata=app_data.loc[:,["name", "date", "time"]].values,
    #                              lat=data["lat"],
    #                              lon=data["lon"],
    #                              marker={"size": 5,
    #                                      "color": COLOR_MAP.get(app),
    #                                      "symbol": "circle",
    #                                      },
    #                              mode="markers",
    #                              name=app,
    #                              )
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
    # TODO: update use of .loc
    dataframe["cw"] = dataframe.loc[:,["year","week"]]\
        .apply(lambda row: f"{row[0]}-{row[1]}-1",
               axis=1)
    dataframe["cw"] = pd.to_datetime(dataframe["cw"],
                                     format="%Y-%W-%w")
    # summarize the amount of activities per week
    data = dataframe.groupby(["app", "year", "week"])["timestamp"]\
        .count().reset_index().rename({"timestamp": summarize_name}, axis=1)
    # rework the calender-week column to be the first day of the week
    # TODO: update use of .loc
    data["calender-week"] = data.loc[:,["year","week"]].apply(lambda row: f"{row[0]}-{row[1]}-1",
                                                              axis=1)
    # TODO: update use of pd.to_datetime
    data["calender-week"] = pd.to_datetime(data["calender-week"],
                                            format="%Y-%W-%w")
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
    data = dataframe.groupby(["sport_type"])["timestamp"]\
        .count().reset_index().rename({"timestamp": "counts"}, axis=1)
    data.sort_values(by="counts",
                     ascending=False,
                     inplace=True)
    # create figure
    pie = pie_figure(data,
                     title=plot_title,
                     height=plot_height)
    return pie


def hours(dataframe: pd.DataFrame,
          plot_height: int):
    plot_title = "Hours"
    # prepare data
    dataframe["timestep"] = dataframe["hour"]*60+dataframe["minutes"]//10
    dataframe["timestep"] = dataframe["timestep"].apply(bu.min2ang)
    dataframe.sort_values(by="timestep",
                          ascending=True,
                          inplace=True)
    dataframe["count"] = 1
    last = None
    count = None
    for index, row in dataframe.loc[:].iterrows():
        step = row["timestep"]
        if step != last:
            last = step
            count = 1
            continue
        count += 1
        dataframe.loc[index,"count"] = count
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
    data = dataframe.loc[(~dataframe["lat"].isna()) &
                         (~dataframe["lon"].isna())
                         ].astype({"year": str})
    lats = []
    lons = []
    colors = []
    names = []
    dates = []
    years = []
    times = []
    for _, row in data.iterrows():
        lats.append(row["lat"])
        lons.append(row["lon"])
        lat, lon = zip(*row["coords"]) # unpack a list of tuples to two lists
        lats.extend(lat)
        lons.extend(lon)
        color = ["Strava"]*(len(lat)+1)
        colors.extend(color)
        name = [row["name"]]*(len(lat)+1)
        names.extend(name)
        date = [row["date"]]*(len(lat)+1)
        dates.extend(date)
        year = [row["year"]]*(len(lat)+1)
        years.extend(year)
        time = [row["time"]]*(len(lat)+1)
        times.extend(time)
        # make a seperation in the lists
        lats.append(None)
        lons.append(None)
        colors.append(None)
        names.append(None)
        dates.append(None)
        years.append(None)
        times.append(None)
    print(len(lats),len(colors))
    # create figure
    worldmap = worldmap_figure(dataframe,
                               title=plot_title,
                               height=plot_height,
                               lat=lats,
                               lon=lons,
                               color=colors,
                               name=names,
                               date=dates,
                               time=times,
                               zoom=0)
    return worldmap


if __name__=="__main__":
    pass
