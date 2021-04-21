"""Plot diagrams for a single hole."""
import gc
import io
import logging
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

__all__ = ["plot_hole"]

BBOX = dict(facecolor="white", alpha=0.75, edgecolor="none", boxstyle="round,pad=0.1")  # text boxes

logger = logging.getLogger("pyinfraformat")


def strip_date(x):
    """Strip str date to datetime."""
    x = str(x)
    try:
        if len(x) == 6:
            date = datetime.strptime(x, "%d%m%y")
        elif len(x) == 8:
            date = datetime.strptime(x, "%d%m%Y")
        else:
            date = pd.to_datetime(x)
    except ValueError:
        date = pd.NaT
    return date


def fig_to_hmtl(fig, clear_memory=True):
    """Transform matplotlib figure to html with mpld3.

    Parameters
    ----------
    fig: matplotlib figure
    clear_memory: bool

    Returns
    -------
    html
    """
    str_io = io.StringIO()
    fig.savefig(str_io, format="svg")
    str_io.seek(0)
    if clear_memory:
        fig.clear()
        plt.close()
        gc.collect()
    return str_io.read()


def plot_po(one_survey):
    """Plot a diagram of PO (Porakonekairaus) with matplotlib.

    Parameters
    ----------
    one_survey : hole object

    Returns
    -------
    figure : matplotlib figure
    """
    df = pd.DataFrame(one_survey.survey.data)
    if "Soil type" in df.columns:  # pylint: disable=unsupported-membership-test
        soils = df.dropna(subset=["Soil type"])
    else:
        soils = None

    fig, (ax_left, ax_right) = plt.subplots(
        1, 2, sharey=True, figsize=(4, 4), gridspec_kw={"wspace": 0, "width_ratios": [2, 2]}
    )
    fig.set_figwidth(4)
    ax_left.step(df["Time (s)"], df["Depth (m)"], where="post", c="k")
    ax_left.invert_yaxis()
    ax_left.spines["top"].set_visible(False)
    ax_left.spines["left"].set_visible(False)
    ax_left.get_yaxis().set_visible(False)
    ax_left.set_xlim([110, 0])
    plt.setp(ax_left.get_yticklabels(), visible=False)

    ax_right.yaxis.set_tick_params(which="both", labelbottom=True)
    ax_right.spines["top"].set_visible(False)
    ax_right.spines["right"].set_visible(False)
    ax_right.spines["bottom"].set_visible(False)
    ax_right.set_xticks([])
    ax_right.set_title(one_survey.header.date.isoformat().split("T")[0])
    ax_left.set_title("{:+.2f}".format(float(one_survey.header["XY"]["Z-start"])))
    ymax_atleast = 5  # hard limit minimum for aestics
    ymax = ax_right.get_ylim()[0]
    if ymax < ymax_atleast:
        ymax = ymax_atleast
    ax_right.set_ylim(ymax, 0)

    if soils is not None:
        for _, row in soils.iterrows():
            ax_right.text(0.03, row["Depth (m)"], s=row["Soil type"], bbox=BBOX)

    last = df["Depth (m)"].iloc[-1]
    # ax_right.plot(0, last, marker="_", zorder=10, clip_on=False, ms=20, c="k")
    ax_right.text(0.03, last, s=one_survey.header["-1"]["Ending"], va="top", bbox=BBOX)
    return fig


def plot_pa(one_survey):
    """Plot a diagram of PA (Painokairaus) with matplotlib.

    Parameters
    ----------
    one_survey : hole object

    Returns
    -------
    figure : matplotlib figure
    """
    df = pd.DataFrame(one_survey.survey.data)
    df.loc[df["Load (kN)"] >= 100, "Load (kN)"] = 0

    fig, (ax_left, ax_right) = plt.subplots(
        1, 2, sharey=True, figsize=(4, 4), gridspec_kw={"wspace": 0, "width_ratios": [1, 3]}
    )
    fig.set_figwidth(4)
    ax_left.step(df["Load (kN)"], df["Depth (m)"], where="post", c="k")
    ax_left.invert_yaxis()
    ax_left.spines["top"].set_visible(False)
    ax_left.spines["left"].set_visible(False)
    ax_left.get_yaxis().set_visible(False)

    plt.setp(ax_left.get_yticklabels(), visible=False)

    ax_left.set_xlim([100, 0])
    ax_right.step(df["Rotation of half turns (-)"], df["Depth (m)"], where="post", c="k")
    ax_right.yaxis.set_tick_params(which="both", labelbottom=True)
    ax_right.spines["top"].set_visible(False)
    ax_right.spines["right"].set_visible(False)
    ax_right.set_xlim([0, 110])
    ax_right.set_title(one_survey.header.date.isoformat().split("T")[0])
    ax_left.set_title("{:+.2f}".format(float(one_survey.header["XY"]["Z-start"])))
    ymax_atleast = 5  # hard limit minimum for aestics
    ymax = ax_right.get_ylim()[0]
    if ymax < ymax_atleast:
        ymax = ymax_atleast
    ax_right.set_ylim(ymax, 0)

    last = df["Depth (m)"].iloc[-1]
    ax_right.plot(0, last, marker="_", zorder=10, clip_on=False, ms=20, c="k")
    ax_right.text(8, last, s=one_survey.header["-1"]["Ending"], va="top", bbox=BBOX)
    return fig


def plot_hp(one_survey):
    """Plot a diagram of HP (Puristinheijarikairaus) with matplotlib.

    Parameters
    ----------
    one_survey : hole object

    Returns
    -------
    figure : matplotlib figure
    """
    df = pd.DataFrame(one_survey.survey.data)

    fig, (ax_left, ax_right) = plt.subplots(
        1, 2, sharey=True, figsize=(4, 4), gridspec_kw={"wspace": 0, "width_ratios": [1, 3]}
    )
    fig.set_figwidth(4)
    ax_left.plot(df["Torque (Nm)"], df["Depth (m)"], c="k")
    ax_left.invert_yaxis()
    ax_left.spines["top"].set_visible(False)
    ax_left.spines["left"].set_visible(False)
    ax_left.get_yaxis().set_visible(False)

    plt.setp(ax_left.get_yticklabels(), visible=False)

    ax_left.set_xlim([200, 0])
    ax_left.set_xticks([200, 100, 0])
    ax_right.barh(
        [0] + list(df["Depth (m)"])[:-1],
        df["Blows"],
        align="edge",
        fill=False,
        height=df["Depth (m)"].diff(periods=1),
        linewidth=1.5,
    )
    ax_right.plot(df["Pressure (MN/m^2)"] * 5, df["Depth (m)"], c="k")

    ax_right.yaxis.set_tick_params(which="both", labelbottom=True)

    ax_right.set_xlim([0, 110])
    ax_right.set_xticks(list(range(0, 120, 20)))
    ymax_atleast = 5  # hard limit minimum for aestics
    ymax = ax_right.get_ylim()[0]
    if ymax < ymax_atleast:
        ymax = ymax_atleast
    ax_right.set_ylim(ymax, 0)

    locs = ax_right.get_xticks()
    y_min, y_max = ax_right.get_ylim()
    y = y_min + (y_max - y_min) * 0.005
    for x in locs[1:]:
        ax_right.text(x, y, s="{:.0f}".format(x / 5), ha="center", va="bottom")

    ax_right.spines["top"].set_visible(False)
    ax_right.spines["right"].set_visible(False)

    ax_right.set_title(one_survey.header.date.isoformat().split("T")[0])
    ax_left.set_title("{:+.2f}".format(float(one_survey.header["XY"]["Z-start"])))

    last = df["Depth (m)"].iloc[-1]
    ax_right.plot(0, last, marker="_", zorder=10, clip_on=False, ms=20, c="k")
    ax_right.text(3, last, s=one_survey.header["-1"]["Ending"], va="top", bbox=BBOX)
    return fig


def plot_si(one_survey):
    """Plot a diagram of SI (Siipikairaus) with matplotlib.

    Parameters
    ----------
    one_survey : hole object

    Returns
    -------
    figure : matplotlib figure
    """
    df = pd.DataFrame(one_survey.survey.data)

    fig, (ax_left, ax_right) = plt.subplots(
        1, 2, sharey=True, figsize=(4, 4), gridspec_kw={"wspace": 0, "width_ratios": [0.5, 3]}
    )
    fig.set_figwidth(4)
    ax_left.invert_yaxis()
    ax_left.spines["top"].set_visible(False)
    ax_left.spines["left"].set_visible(False)
    ax_left.get_yaxis().set_visible(False)
    ax_left.set_xticks([])

    plt.setp(ax_left.get_yticklabels(), visible=False)
    ax_left.set_xlim([100, 0])

    for i in range(len(df) - 1):
        depth = list(df.iloc[[i, i + 1]]["Depth (m)"])
        depth.insert(0, depth[0])
        depth.append(depth[-1])
        strength = list(df.iloc[[i, i + 1]]["Shear strenght (kN/m^2)"])
        strength.insert(0, 0)
        strength.append(0)
        ax_right.plot(strength, depth, c="k")

    ax_right.plot(df["Residual Shear strenght (kN/m^2)"], df["Depth (m)"], c="k", ls="--")
    ax_right.yaxis.set_tick_params(which="both", labelbottom=True)
    ax_right.spines["top"].set_visible(False)
    ax_right.spines["right"].set_visible(False)
    ax_right.set_xlim([0, 60])
    ax_right.set_xticks(list(range(0, 70, 10)))
    ax_right.set_title(one_survey.header.date.isoformat().split("T")[0])
    ax_left.set_title("{:+.2f}".format(float(one_survey.header["XY"]["Z-start"])))
    ymax_atleast = 5  # hard limit minimum for aestics
    ymax = ax_right.get_ylim()[0]
    if ymax < ymax_atleast:
        ymax = ymax_atleast
    ax_right.set_ylim(ymax, 0)

    last = df["Depth (m)"].iloc[-1]
    ax_right.plot(0, last, marker="_", zorder=10, clip_on=False, ms=20, c="k")
    ax_right.text(3, last, s=one_survey.header["-1"]["Ending"], va="top", bbox=BBOX)
    return fig


def plot_tr(one_survey):
    """Plot a diagram of TR (Tärykairaus) with matplotlib.

    Parameters
    ----------
    one_survey : hole object

    Returns
    -------
    figure : matplotlib figure
    """
    df = pd.DataFrame(one_survey.survey.data)
    if "Soil type" in df.columns:  # pylint: disable=unsupported-membership-test
        soils = df.dropna(subset=["Soil type"])
    else:
        soils = None

    fig, (ax_left, ax_right) = plt.subplots(
        1, 2, sharey=True, figsize=(4, 4), gridspec_kw={"wspace": 0, "width_ratios": [2, 2]}
    )
    fig.set_figwidth(4)
    ax_left.invert_yaxis()
    ax_left.spines["top"].set_visible(False)
    ax_left.spines["left"].set_visible(False)
    ax_left.spines["bottom"].set_visible(False)
    ax_left.set_xticks([])
    ax_left.get_yaxis().set_visible(False)
    plt.setp(ax_left.get_yticklabels(), visible=False)

    ax_right.yaxis.set_tick_params(which="both", labelbottom=True)
    ax_right.spines["top"].set_visible(False)
    ax_right.spines["right"].set_visible(False)
    ax_right.spines["bottom"].set_visible(False)
    ax_right.set_xlim(0, 1)
    ax_right.set_xticks([])
    ax_right.set_title(one_survey.header.date.isoformat().split("T")[0])
    ax_left.set_title("{:+.2f}".format(float(one_survey.header["XY"]["Z-start"])))
    ymax_atleast = 5  # hard limit minimum for aestics
    ymax = df["Depth (m)"].iloc[-1]
    if ymax < ymax_atleast:
        ymax = ymax_atleast
    ax_right.set_ylim(ymax, 0)

    if soils is not None:
        for _, row in soils.iterrows():
            ax_right.text(0.03, row["Depth (m)"], s=row["Soil type"], va="bottom", bbox=BBOX)

    last = df["Depth (m)"].iloc[-1]
    ax_right.plot(0, last, marker="_", zorder=10, clip_on=False, ms=20, c="k")
    ax_right.text(0.10, last, s=one_survey.header["-1"]["Ending"], va="top", bbox=BBOX)

    return fig


def plot_he(one_survey):
    """Plot a diagram of HE (Heijarikairaus) with matplotlib.

    Parameters
    ----------
    one_survey : hole object

    Returns
    -------
    figure : matplotlib figure
    """
    df = pd.DataFrame(one_survey.survey.data)
    if "Soil type" in df.columns:  # pylint: disable=unsupported-membership-test
        soils = df.dropna(subset=["Soil type"])
    else:
        soils = None
    fig, (ax_left, ax_right) = plt.subplots(
        1, 2, sharey=True, figsize=(4, 4), gridspec_kw={"wspace": 0, "width_ratios": [1, 3]}
    )
    fig.set_figwidth(4)
    ax_left.invert_yaxis()
    ax_left.spines["top"].set_visible(False)
    ax_left.spines["left"].set_visible(False)
    ax_left.get_yaxis().set_visible(False)
    plt.setp(ax_left.get_yticklabels(), visible=False)
    ax_left.set_xticks([])
    ax_right.barh(
        [0] + list(df["Depth (m)"])[:-1],
        df["Blows"],
        align="edge",
        fill=False,
        height=df["Depth (m)"].diff(periods=1),
        linewidth=1.5,
    )
    ax_right.yaxis.set_tick_params(which="both", labelbottom=True)
    ax_right.set_xlim([0, 110])
    ax_right.set_xticks(list(range(0, 120, 20)))
    ymax_atleast = 5  # hard limit minimum for aestics
    ymax = ax_right.get_ylim()[0]
    if ymax < ymax_atleast:
        ymax = ymax_atleast
    ax_right.set_ylim(ymax, 0)

    ax_right.spines["top"].set_visible(False)
    ax_right.spines["right"].set_visible(False)

    ax_right.set_title(one_survey.header.date.isoformat().split("T")[0])
    ax_left.set_title("{:+.2f}".format(float(one_survey.header["XY"]["Z-start"])))

    last = df["Depth (m)"].iloc[-1]
    ax_right.plot(0, last, marker="_", zorder=10, clip_on=False, ms=20, c="k")
    ax_right.text(8, last, s=one_survey.header["-1"]["Ending"], va="top", bbox=BBOX)

    if soils is not None:
        for _, row in soils.iterrows():
            ax_right.text(3, row["Depth (m)"], s=row["Soil type"], bbox=BBOX)

    return fig


def plot_vp(one_survey):
    """Plot a diagram of VP (Pohjavesiputki) or VO (Orsivesiptki) with matplotlib.

    Parameters
    ----------
    one_survey : hole object

    Returns
    -------
    figure : matplotlib figure
    """
    df = pd.DataFrame(one_survey.survey.data)

    bottom_level = df["Bottom level of pipe"][0]
    top_level = df["Top level of pipe"][0]
    ground_level = one_survey.header.XY["Z-start"]
    sieve_length = df["Lenght of the sieve(m)"][0]

    dates = df["Date"].apply(strip_date)
    fig, (ax_left, ax_right) = plt.subplots(
        1, 2, sharey=True, figsize=(4, 4), gridspec_kw={"wspace": 0, "width_ratios": [1, 3]}
    )

    rect_sieve = patches.Rectangle(
        (0.45, bottom_level), width=0.2, height=sieve_length, linewidth=1, fill=None, hatch="///"
    )
    rect_rest = patches.Rectangle(
        (0.45, bottom_level + sieve_length),
        width=0.2,
        height=((top_level - bottom_level) - sieve_length),
        linewidth=1,
        fill=None,
    )
    try:
        level_min = df["Water level"].min()
    except KeyError:
        level_min = 1
    if bottom_level > level_min:
        ax_left.set_ylim(level_min, top_level)
    else:
        if bottom_level < top_level:
            ax_left.set_ylim(bottom_level, top_level)
        else:
            ax_left.set_ylim(top_level - 2, top_level)

    ax_left.set_xlim(0, 1.5)
    ax_left.add_patch(rect_sieve)
    ax_left.add_patch(rect_rest)
    ax_left.set_title("{:+.2f}".format(ground_level))
    ax_left.plot(ax_left.get_xlim(), [ground_level, ground_level], c="k")
    ax_left.set_xticks([])
    plt.setp(ax_left.get_yticklabels(), visible=False)

    ax_right.yaxis.set_tick_params(which="both", labelbottom=True)
    counts = dates.value_counts()
    if len(counts) <= 1:
        ax_right.plot(df["Water level"], "o-")
        ax_right.text(
            0.02,
            0.01,
            "Dates missing, n: {}".format(len(dates)),
            transform=ax_right.transAxes,
            bbox=BBOX,
        )
        if len(dates) < 5:
            ax_right.set_xticks(range(len(dates)))
    else:
        ax_right.plot(dates, df["Water level"], "o-")
        ax_right.set_title(one_survey.header.date.isoformat().split("T")[0])
        ax_right.set_xticks(np.linspace(*ax_right.get_xlim(), 3))
        ax_right.set_xticklabels(
            [mdates.num2date(label).isoformat()[:10] for label in ax_right.get_xticks()]
        )
    return fig


def plot_hole(one_survey, output="figure", figsize=(4, 4)):
    """Plot a diagram of a sounding with matplotlib.

    Parameters
    ----------
    one_survey : hole object
    output : str
        Possible values: ['figure', 'svg']
    figsize : tuple
        figure size in inches

    Returns
    -------
    figure : figure or svg
    """

    def _plot_hole(one_survey):
        hole_type = one_survey.header["TT"]["Survey abbreviation"]

        if len(one_survey.survey.data) == 0:
            fig = plt.figure()
        elif hole_type == "PO":
            fig = plot_po(one_survey)
        elif hole_type == "PA":
            fig = plot_pa(one_survey)
        elif hole_type == "HP":
            fig = plot_hp(one_survey)
        elif hole_type == "SI":
            fig = plot_si(one_survey)
        elif hole_type == "TR":
            fig = plot_tr(one_survey)
        elif hole_type == "HE":
            fig = plot_he(one_survey)
        elif hole_type == "VP":
            fig = plot_vp(one_survey)
        elif hole_type == "VO":
            fig = plot_vp(one_survey)
        else:
            raise NotImplementedError('Hole object "{}" not supported'.format(hole_type))
        fig.tight_layout()
        fig.set_size_inches(figsize)
        return fig

    try:
        fig = _plot_hole(one_survey)
    except (KeyError, TypeError) as error:
        logger.warning("Data missing, check hole. %s", error)
        plt.close()
        raise

    if output == "figure":
        return fig
    elif output == "svg":
        return fig_to_hmtl(fig)
    else:
        raise NotImplementedError("Plotting backend {} not implemented".format(output))
