# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""
# Standard library

# Third party
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
# Local imports
from backend import utils

TEMPLATE = "plotly_dark"
COLOR_MAP = {"Strava": "#FC4C02", # the color of the Strava app
             }
LEFT_RIGHT_MARGIN = 15
TOP_BOTTOM_MARGIN = 25


def empty_figure(title: str,
                 height: int) -> go.Figure:
    """
    Create an empty figure with the title and a text label to show that no data is
    available to display.

    Parameters
    ----------
    title : str
        The title of the replaced figure.
    height : int
        The desired height of the figure.

    Returns
    -------
    figure : go.Figure
        An empty figure with .

    """
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


def timeline(dataframe: pd.DataFrame,
             height:int) -> go.Figure:
    """


    Parameters
    ----------
    dataframe : pd.DataFrame
        DESCRIPTION.
    height : int
        The desired height of the figure.

    Returns
    -------
    figure : go.Figure
        DESCRIPTION.

    """
    plot_title = "Timeline of all the activities"

    # show empty figure if no data is provided
    if dataframe.empty:
        return empty_figure(plot_title, height)

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
    data["calender-week"] = pd.to_datetime(data["calender-week"],
                                            format="%Y-%W-%w")

    # create figure
    figure = px.area(data_frame=data,
                     x="calender-week",
                     y=summarize_name,
                     line_group="app",
                     color="app",
                     hover_name=None,
                     hover_data={"app": False,
                                 "calender-week": False,
                                 summarize_name: False
                                 },
                     custom_data=["app"],
                     color_discrete_map=COLOR_MAP,
                     orientation="v", # orient the chart
                     line_shape="spline", # smoothes out the line
                     title=plot_title,
                     template=TEMPLATE,
                     height=height
                     )
    figure.update_traces(hovertemplate="Activity on %{customdata[0]}"
                         )
    figure.update_layout(showlegend=False,
                         margin={"l": LEFT_RIGHT_MARGIN,
                                 "r": LEFT_RIGHT_MARGIN,
                                 "t": TOP_BOTTOM_MARGIN,
                                 "b": TOP_BOTTOM_MARGIN},
                         yaxis={"tickmode": "linear",
                                "tick0": 0,
                                "dtick": 5})
    figure.add_scatter(customdata=dataframe.loc[:,["name","date"]].values,
                       hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}",
                       marker={"size": 3},
                       mode="markers", # select drawing mode
                       name="", # set trace name to empty
                       opacity=1,
                       x=dataframe["cw"], # position the dots by week
                       y=dataframe["pos"],
                       )
    return figure


def days(dataframe: pd.DataFrame,
         height:int) -> go.Figure:
    """


    Parameters
    ----------
    dataframe : pd.DataFrame
        DESCRIPTION.
    height : int
        The desired height of the figure.

    Returns
    -------
    figure : TYPE
        DESCRIPTION.

    """
    plot_title = "Frequency of the weekdays"
    # show empty figure if no data is provided
    if dataframe.empty:
        return empty_figure(plot_title, height)

    # prepare data
    data = dataframe.groupby(["app","weekday"])["time"]\
            .count().reset_index().rename({"time": "counts"}, axis=1)
    data["percentage"] = data["counts"] / dataframe.shape[0]
    hover_data = [day for num, day in enumerate(["Monday",
                                                 "Tuesday",
                                                 "Wednesday",
                                                 "Thursday",
                                                 "Friday",
                                                 "Saturday",
                                                 "Sunday"]) if num in data.weekday]

    # create figure
    figure = px.bar(data_frame=data,
                    x="weekday",
                    y="percentage",
                    color="app",
                    color_discrete_map=COLOR_MAP,
                    hover_data=[hover_data,
                                ],
                    text_auto=".0%",
                    title=plot_title,
                    template=TEMPLATE,
                    height=height,
                    )
    figure.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>%{y}"
                         )
    figure.update_layout(showlegend=False,
                         margin={"l": LEFT_RIGHT_MARGIN,
                                 "r": LEFT_RIGHT_MARGIN,
                                 "t": TOP_BOTTOM_MARGIN,
                                 "b": TOP_BOTTOM_MARGIN},
                         xaxis = {"tickmode":"array",
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
    return figure


def hours(dataframe: pd.DataFrame,
          height:int) -> go.Figure:
    """


    Parameters
    ----------
    dataframe : pd.DataFrame
        DESCRIPTION.
    height : int
        The desired height of the figure.

    Returns
    -------
    figure : TYPE
        DESCRIPTION.

    """
    plot_title = "Starting time of the activities"

    # show empty figure if no data is provided
    if dataframe.empty:
        return empty_figure(plot_title, height)

    # prepare data
    dataframe["timestep"] = dataframe["hour"]*60+dataframe["minutes"]//10
    dataframe["timestep"] = dataframe["timestep"].apply(utils.min2ang)
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
    figure = px.scatter_polar(data_frame=dataframe,
                              r="count",
                              theta="timestep",
                              color="app",
                              hover_name="name",
                              custom_data=["name","time"],
                              color_discrete_map=COLOR_MAP,
                              direction="clockwise",
                              start_angle=90, #start at due north
                              title=plot_title,
                              template=TEMPLATE,
                              height=height
                              )
    figure.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}"
                         )
    max_axis = 0 if dataframe.empty else int(dataframe["count"].max())
    figure.update_layout(showlegend=False,
                         margin={"l": LEFT_RIGHT_MARGIN,
                                 "r": LEFT_RIGHT_MARGIN,
                                 "t": TOP_BOTTOM_MARGIN,
                                 "b": TOP_BOTTOM_MARGIN},
                         polar={"radialaxis": {"tickvals":
                                               list(range(0, max_axis+1, 5))},
                                "angularaxis": {"tickvals":
                                                [utils.hr2ang(hr) for hr in range(24)],
                                                "ticktext":
                                                    [str(24 if hr==0 else hr) for hr in range(24)]}
                                }
                         )
    return figure


def types(dataframe: pd.DataFrame,
          height:int) -> go.Figure:
    """


    Parameters
    ----------
    dataframe : pd.DataFrame
        DESCRIPTION.
    height : int
        The desired height of the figure.

    Returns
    -------
    figure : TYPE
        DESCRIPTION.

    """
    plot_title = "Subdivision of workout types"
    # show empty figure if no data is provided
    if dataframe.empty:
        return empty_figure(plot_title, height)

    # prepare data
    data = dataframe.groupby(["sport_type"])["timestamp"]\
        .count().reset_index().rename({"timestamp": "counts"}, axis=1)
    data.sort_values(by="counts",
                     ascending=False,
                     inplace=True)

    # create figure
    figure = px.pie(data_frame=data,
                    names="sport_type",
                    values="counts",
                    color="sport_type",
                    # reverse the color sequence
                    color_discrete_sequence=px.colors.sequential.Oranges_r,
                    title=plot_title,
                    template=TEMPLATE,
                    height=height,
                    hole=.3 # make it a donut
                    )
    figure.update_traces(textposition='inside', # set the percentage inside the chart
                         # show the category and the amount in the chart
                         textinfo="label+percent",
                         hovertemplate="<b>%{label}</b><br>%{value}"
                         )
    figure.update_layout(showlegend=False,
                         margin={"l": LEFT_RIGHT_MARGIN,
                                 "r": LEFT_RIGHT_MARGIN,
                                 "t": TOP_BOTTOM_MARGIN,
                                 "b": TOP_BOTTOM_MARGIN},
                         )
    return figure


def locations(dataframe: pd.DataFrame,
              height:int) -> go.Figure:
    """


    Parameters
    ----------
    dataframe : pd.DataFrame
        DESCRIPTION.
    height : int
        The desired height of the figure.

    Returns
    -------
    figure : TYPE
        DESCRIPTION.

    """
    plot_title = "Location of activities"
    # show empty figure if no data is provided
    if dataframe.empty:
        return empty_figure(plot_title, height)

    # prepare data
    data = dataframe.loc[(~dataframe["lat"].isna()) &
                         (~dataframe["lon"].isna())
                         ].astype({"year": str})
    zoom = utils.determine_zoom(data.lat.to_list(), data.lon.to_list())
    lats = []
    lons = []
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
        names.append(None)
        dates.append(None)
        years.append(None)
        times.append(None)

    # create figure
    figure = px.line_mapbox(data_frame=data,
                            lat=lats,
                            lon=lons,
                            color=["Strava"]*len(lats),
                            hover_name=names,
                            custom_data=[names, dates, times],
                            color_discrete_map=COLOR_MAP,
                            zoom=zoom,
                            center={"lat": dataframe.lat.median(),
                                    "lon": dataframe.lon.median()
                                    },
                            mapbox_style="carto-darkmatter",
                            title=plot_title,
                            template=TEMPLATE,
                            height=height
                            )
    for app in (groups:=data.groupby("app").groups):
        app_data = data.loc[groups[app].values]
        figure.add_scattermapbox(below="traces",
                                 customdata=app_data.loc[:,["name", "date", "time"]].values,
                                 lat=data["lat"],
                                 lon=data["lon"],
                                 marker={"size": 5,
                                         "color": COLOR_MAP.get(app),
                                         "symbol": "circle",
                                         },
                                 mode="markers",
                                 name=app,
                                 )
    figure.update_traces(hovertemplate="<br>".join(["<b>%{customdata[0]}</b>",
                                                    "%{customdata[1]}",
                                                    "%{customdata[2]}",
                                                    "(%{lat},%{lon})",
                                                    ],
                                                    ),
                          )
    figure.update_layout(showlegend=False,
                         margin={"l": LEFT_RIGHT_MARGIN,
                                 "r": LEFT_RIGHT_MARGIN,
                                 "t": TOP_BOTTOM_MARGIN,
                                 "b": TOP_BOTTOM_MARGIN},
                         )
    return figure


if __name__ == "__main__":
    pass
