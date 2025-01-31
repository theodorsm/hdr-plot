#
# hdr-plot.py v0.2.3 - A simple HdrHistogram plotting script.
# Copyright © 2018 Bruno Bonacci - Distributed under the Apache License v 2.0
#
# usage: hdr-plot.py [-h] [--output OUTPUT] [--title TITLE] [--nobox] files [files ...]
#
# A standalone plotting script for https://github.com/giltene/wrk2 and
#  https://github.com/HdrHistogram/HdrHistogram.
#
# This is just a quick and unsophisticated script to quickly plot the
# HdrHistograms directly from the output of `wkr2` benchmarks.
#
#
import argparse
import re
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


#
# parsing and plotting functions
#

regex = re.compile(r"\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)")
filename = re.compile(r"(.*/)?([^.]*)(\.\w+\d+)?")


def parse_percentiles(file):
    lines = [line for line in open(file) if re.match(regex, line)]
    values = [re.findall(regex, line)[0] for line in lines]
    pctles = [(float(v[0]), float(v[1]), int(v[2]), float(v[3])) for v in values]
    percentiles = pd.DataFrame(
        pctles, columns=["Latency", "Percentile", "TotalCount", "inv-pct"]
    )
    return percentiles


def parse_files(files):
    return [parse_percentiles(file) for file in files]


def info_text(name, data, jitter):
    textstr = (
        "%-18s\n------------------\n%-6s = %6.3f ms\n%-6s = %6.3f ms\n%-6s = %6.3f ms\n%-6s = %6.0f us\n"
        % (
            name,
            "min",
            data["Latency"].min(),
            "median",
            data.iloc[(data["Percentile"] - 0.5).abs().argsort()[:1]]["Latency"],
            "max",
            data["Latency"].max(),
            "jitter",
            jitter,
        )
    )
    return textstr


def info_box(ax, text):
    props = dict(boxstyle="round", facecolor="lightcyan", alpha=0.5)

    ax.text(
        #    0.05,
        #    0.95,
        1.01,
        0.95,
        text,
        transform=ax.transAxes,
        verticalalignment="top",
        bbox=props,
        fontname="monospace",
    )


def plot_summarybox(ax, percentiles, jitters, labels):
    # add info box to the side
    textstr = "\n".join(
        [info_text(labels[i], percentiles[i], jitters[i]) for i in range(len(labels))]
    )
    info_box(ax, textstr)


def plot_percentiles(percentiles, labels):
    fig, ax = plt.subplots(figsize=(18, 10))
    # plot values
    for data in percentiles:
        ax.plot(data["Percentile"], data["Latency"])

    # set axis and legend
    ax.grid()
    ax.set(
        xlabel="Percentile",
        ylabel="Latency (milliseconds)",
        title="Latency Percentiles (lower is better)",
    )
    ax.set_xscale("logit")
    plt.xticks([0.25, 0.5, 0.9, 0.99, 0.999, 0.9999, 0.99999, 0.999999])
    majors = ["25%", "50%", "90%", "99%", "99.9%", "99.99%", "99.999%", "99.9999%"]
    ax.xaxis.set_major_formatter(ticker.FixedFormatter(majors))
    ax.xaxis.set_minor_formatter(ticker.NullFormatter())
    plt.legend(
        bbox_to_anchor=(0.0, 1.02, 1.0, 0.102),
        loc=3,
        ncol=2,
        borderaxespad=0.0,
        labels=labels,
    )

    return fig, ax


def arg_parse():
    parser = argparse.ArgumentParser(description="Plot HDRHistogram latencies.")
    parser.add_argument("files", nargs="+", help="list HDR files to plot")
    parser.add_argument("--jitters", type=str, help="delimited list jitters to plot")
    parser.add_argument(
        "--output",
        default="latency.png",
        help="Output file name (default: latency.png)",
    )
    parser.add_argument("--title", default="", help="The plot title.")
    parser.add_argument("--nobox", help="Do not plot summary box", action="store_true")
    args = parser.parse_args()
    return args


def main():
    # print command line arguments
    args = arg_parse()

    # load the data and create the plot
    pct_data = parse_files(args.files)
    jitters = [int(item) for item in args.jitters.split(",")]
    labels = [re.findall(filename, file)[0][1] for file in args.files]
    # plotting data
    fig, ax = plot_percentiles(pct_data, labels)
    # plotting summary box
    if not args.nobox:
        plot_summarybox(ax, pct_data, jitters, labels)
    # add title
    plt.suptitle(args.title)
    # save image
    plt.savefig(args.output)
    print("Wrote: " + args.output)


# for testing
if __name__ == "__main__":
    main()
