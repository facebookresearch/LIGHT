#!/usr/bin/env python3


# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import argparse
import sys
import os

from yappi import get_func_stats, COLUMNS_FUNCSTATS, COLUMNS_THREADSTATS
import yappi
import deploy.web.server.run_server as server

"""
This script launches the server from default config with a profiler wrapped around it to
monitor resource usage
"""


def main():
    parser = argparse.ArgumentParser(description="Profile the game server")
    parser.add_argument(
        "--sort-type",
        type=str,
        default="ttot",
        help="Number of lines to print from the profiler per thread",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Number of lines to print from the profiler per thread",
    )
    parser.add_argument("--output", type=str, help="File (relative) path to dump data")
    args, _ = parser.parse_known_args()
    limit = args.limit
    sort_type = args.sort_type
    if args.output is not None:
        out_place = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), args.output + ".profile"
        )
        out = open(out_place, "w")
    else:
        out = sys.stdout

    profile_server(sort_type, out, limit)
    out.close()


def profile_server(sort_type, out, limit):
    """
    The main wrapper for calling the server and processing the stats for each thread
    """
    yappi.set_clock_type("wall")
    yappi.start()
    server.main()
    yappi.stop()

    threads = yappi.get_thread_stats()
    for thread in threads:
        stats = yappi.get_func_stats(ctx_id=thread.id).sort(sort_type)
        print_all(thread, stats, out, limit=limit)


def print_all(thread, stats, out, limit=None):
    """
    Writes all data for thread stats to out, with limit number of lines and all other truncated
    """
    if stats.empty():
        return
    sizes = [60, 10, 8, 8, 8]
    columns = dict(zip(range(len(COLUMNS_FUNCSTATS)), zip(COLUMNS_FUNCSTATS, sizes)))
    show_stats = stats
    if limit:
        show_stats = stats[:limit]
    out.write(
        "Function stats for (%s) (%d), time of: (%.5f) and scheduled (%d) times"
        % (thread.name, thread.id, thread.ttot, thread.sched_count)
    )
    out.write(os.linesep)
    names = "%-*s %-*s %-*s %-*s %-*s" % (
        sizes[0],
        "names",
        sizes[1],
        "ncalls",
        sizes[2],
        "ttot",
        sizes[3],
        "tsub",
        sizes[4],
        "tavg",
    )
    out.write(names)
    out.write(os.linesep)
    for stat in show_stats:
        stat._print(out, columns)
    out.write(os.linesep)


if __name__ == "__main__":
    main()
