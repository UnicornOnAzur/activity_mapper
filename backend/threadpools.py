# -*- coding: utf-8 -*-
"""
@author: QtyPython2020

"""

# Standard library
import concurrent
import queue
import threading
import time
# Third party
import pandas as pd
import streamlit as st
# Local imports
import backend

# TODO: fix import so it always retreives all pages
def thread_get_and_parse(token) -> pd.DataFrame:
    # create the shared queues
    task1_queue_in = queue.Queue()
    task1_queue_out = queue.Queue()
    task2_queue_out = queue.Queue()
    #
    barrier1 = threading.Barrier(5)
    barrier2 = threading.Barrier(10)
    #
    results = []
    i = 1
    # create the thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as threadpool:
        # issue task 1 workers
        _ = [threadpool.submit(backend.get_activities_page, task1_queue_in, task1_queue_out, barrier1, token)
             for _ in range(5)]
        # issue task 2 workers
        _ = [threadpool.submit(backend.parse_page, task1_queue_out, task2_queue_out, barrier2)
             for _ in range(10)]
        for thread in threadpool._threads:
            st.runtime.scriptrunner.add_script_run_ctx(thread)
        # push work into task 1
        while True:
            task1_queue_in.put(i)
            i += 1
            time.sleep(1)
            if None in task1_queue_in.queue:
                # signal that there is no more work
                task1_queue_in.put(None)
                break
        # consume results
        while True:
            # retrieve data
            data = task2_queue_out.get()
            # check for the end of work
            if data is None:
                # stop processing
                break
            # <>
            results.append(pd.DataFrame.from_dict(data,orient="index") if isinstance(data, dict) else data)
    total = pd.concat(results,
                      ignore_index=True)
    total.sort_values("timestamp",
                      inplace=True)
    return total


if __name__ == "__main__":
    pass
