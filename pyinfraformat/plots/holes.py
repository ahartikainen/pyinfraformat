"""Plot diagrams for a single hole."""
import gc
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import mpld3

__all__ = ["plot_hole"]

BBOX = dict(facecolor="white", alpha=0.75, edgecolor="none", boxstyle="round,pad=0.1")  # text boxes


def convert_numpy(obj):
    """Convert numpy float or int to python."""
    if isinstance(
        obj,
        (
            np.int_,
            np.intc,
            np.intp,
            np.int8,
            np.int16,
            np.int32,
            np.int64,
            np.uint8,
            np.uint16,
            np.uint32,
            np.uint64,
        ),
    ):
        return int(obj)
    elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
        return float(obj)
    return json.JSONEncoder().default(obj)


def fig_to_hmtl(fig, clear_memory=True):
    """Transform matplotlib figure to html with mpld3.

    Parameters
    ----------
    fig: matplotlib figure

    Returns
    -------
    html
    """
    # mpld3.plugins.clear(fig)
    html = mpld3.fig_to_html(
        fig, no_extras=True, template_type="simple", d3_url=r"https://d3js.org/d3.v3.min.js"
    )
    emtpy_html = (
        html[: html.find("{", html.find("{") + 1)]
        + "{replace}"
        + html[html.rfind("}", 0, html.rfind("}") - 1) + 1 :]
    )
    figure_dict = mpld3.fig_to_dict(fig)

    left, _ = figure_dict["axes"]
    del left["axes"][1]

    figure_json = json.dumps(figure_dict, default=convert_numpy)

    if clear_memory:
        fig.clear()
        plt.close()
        gc.collect()

    return emtpy_html.replace("{replace}", figure_json)


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


def plot_hole(one_survey, backend="matplotlib"):
    """Plot a diagram of a sounding with matplotlib.

    Parameters
    ----------
    one_survey : hole object
    backend : str
        Backend to plot with
        possible values 'mpld3' and 'matplotlib'

    Returns
    -------
    figure : matplotlib figure or mpld3 html
    """
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
    else:
        raise NotImplementedError('Hole object "{}" not supported'.format(hole_type))
    fig.tight_layout()
    if backend == "matplotlib":
        return fig
    elif backend == "mpld3":
        return fig_to_hmtl(fig)
    else:
        raise NotImplementedError("Plotting backend {} not implemented".format(backend))
