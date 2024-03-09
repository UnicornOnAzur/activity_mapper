# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

The two threadpools used in the app and the worker functions.
"""

# Standard library
import concurrent.futures as c_futures
import queue
import threading
import time
import typing
# Third party
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
# Local imports
import backend


def get_activities_page(queue_in: queue.Queue,
                        queue_out: queue.Queue,
                        barrier: threading.Barrier,
                        access_token: str) -> None:
    """
    Function for worker group 1 to retreive one page at a time until the
    response length is zero or the input is None.

    Parameters
    ----------
    queue_in : queue.Queue
        The queue providing the request_page_num.
    queue_out : queue.Queue
        The queue receiving the retrieved page.
    barrier : threading.Barrier
        Barrier object to make all workers wait to complete execution.
    access_token : str
        The Strava access token.

    Returns
    -------
    None.

    """
    # loop forever until shutdown signal is given
    while True:
        # read item from queue
        request_page_num: typing.Union[int | None] = queue_in.get()
        # prepare header and param
        header: dict = {"Authorization": f"Bearer {access_token}"}
        param: dict = {"per_page": 100, "page": request_page_num}
        # send get request for the desired page
        response: typing.Union[list[dict] | dict] = backend.get_request(
            url=backend.ACTIVITIES_LINK,
            headers=header,
            params=param
                                                                        )
        # check for shutdown
        if request_page_num is None or len(response) == 0:
            # put signal back on queue
            queue_in.put(None)
            # wait on the barrier for all other workers
            barrier.wait()
            # send signal on output queue
            queue_out.put(None)
            # stop processing
            break
        # push result onto queue
        queue_out.put(response)


def parse_page(queue_in: queue.Queue,
               queue_out: queue.Queue,
               barrier: threading.Barrier) -> None:
    """
    Function for worker group 2 to parse one page at a time until the input is
    None or a dict which signals a propagated error message.

    Parameters
    ----------
    queue_in : queue.Queue
        The queue providing the retrieved data.
    queue_out : queue.Queue
        The queue receiving the parsed data.
    barrier : threading.Barrier
        Barrier object to make all workers wait to complete execution.

    Returns
    -------
    None
        DESCRIPTION.

    """
    # loop forever until shutdown signal is given
    while True:
        # read item from queue
        data: typing.Union[list[dict] | dict | None] = queue_in.get()
        # check for shutdown
        if data is None or isinstance(data, dict):
            # put signal back on queue
            queue_in.put(None)
            # wait on the barrier for all other workers
            barrier.wait()
            # send signal on output queue
            queue_out.put(data if isinstance(data, dict) else None)
            # stop processing
            break
        # parse the retrieved data
        parsed_data: pd.DataFrame = backend.parse(data)
        # push result onto queue
        queue_out.put(parsed_data)


def thread_get_and_parse(token: str) -> pd.DataFrame:
    """
    Use threading to speed up sending get requests and parse the responses.

    Parameters
    ----------
    token : str
        Strava access token.

    Returns
    -------
    total : pd.DataFrame
        Table of all the retrieved activities.

    """
    #
    results: list = []
    page_num: int = 1
    worker_group_1: int = 5
    worker_group_2: int = 10
    total: int = worker_group_1 + worker_group_2
    # create the shared queues
    task1_queue_in: queue.Queue = queue.Queue()
    task1_queue_out: queue.Queue = queue.Queue()
    task2_queue_out: queue.Queue = queue.Queue()
    # create the barriers
    barrier1: threading.Barrier = threading.Barrier(worker_group_1)
    barrier2: threading.Barrier = threading.Barrier(worker_group_2)
    # create the thread pool
    with c_futures.ThreadPoolExecutor(max_workers=total) as threadpool:
        # issue get_activities_page to first group of workers
        _ = [threadpool.submit(backend.get_activities_page,
                               task1_queue_in,
                               task1_queue_out,
                               barrier1,
                               token)
             for _ in range(worker_group_1)]
        # issue parse_page to second group of workers
        _ = [threadpool.submit(backend.parse_page,
                               task1_queue_out,
                               task2_queue_out,
                               barrier2)
             for _ in range(worker_group_2)]
        # add ScriptRunContext to threads
        for thread in threadpool._threads:
            st.runtime.scriptrunner.add_script_run_ctx(thread)
        # push work into first group
        while True:
            # get result from selected page number
            task1_queue_in.put(page_num)
            page_num += 1
            # wait to give other workers time to provide response
            time.sleep(1)
            if None in task1_queue_in.queue:
                # signal that there is no more work
                task1_queue_in.put(None)
                break
        # consume results
        while True:
            # retrieve data
            data: typing.Union[None | dict | pd.DataFrame] =\
                task2_queue_out.get()
            # check for the end of work
            if data is None:
                # stop processing
                break
            # <>
            results.append(pd.DataFrame.from_dict(data,
                                                  orient="index")
                           if isinstance(data, dict) else data)
    total: pd.DataFrame = pd.DataFrame(columns=backend.STRAVA_COLS)\
        if not results else pd.concat(results,
                                      ignore_index=True)
    total.sort_values("timestamp",
                      inplace=True)
    return total


def thread_create_figures(df: pd.DataFrame,
                          creation: str) -> list[go.Figure]:
    """
    Use threading to speed up creating the figures.

    Parameters
    ----------
    df : pd.DataFrame
        Table of all the retrieved activities.
    creation : str
        Input for the vertical line in the days plot.

    Returns
    -------
    figures : list[go.Figure]
        List of all the plotly figures.

    """
    with c_futures.ThreadPoolExecutor() as threadpool:
        figures: list = []
        futures: list = [threadpool.submit(backend.timeline,
                                           **{"original": df,
                                              "plot_height":
                                                  backend.TOP_ROW_HEIGHT,
                                              "creation": creation
                                              }
                                           )
                         ]
        for func, height in zip([backend.days,
                                 backend.locations,
                                 backend.types,
                                 backend.hours
                                 ],
                                [backend.BOTTOM_ROW_HEIGHT//3-50,
                                 backend.BOTTOM_ROW_HEIGHT,
                                 backend.BOTTOM_ROW_HEIGHT//1.5,
                                 backend.BOTTOM_ROW_HEIGHT//1.5
                                 ]
                                ):
            futures.append(threadpool.submit(func,
                                             **{"original": df,
                                                "plot_height": height
                                                }
                                             )
                           )
        for future in futures:
            figures.append(future.result())
    return figures


if __name__ == "__main__":
    pass
