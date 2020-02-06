"""Plot diagrams for a single hole."""
import gc
import mpld3
import pandas as pd
import matplotlib.pyplot as plt


def fig_to_hmtl(fig, clear_memory=True):
    """Transform matplotlib figure to html with mpld3.

    Parameters
    ----------
    fig: matplotlib figure

    Returns
    -------
    html : str
    """
    html = mpld3.fig_to_html(fig, no_extras=True, template_type="simple")
    if len(fig.axes) == 2:  # remove left axes scale
        html = (
            html[0 : html.find(', {"position": "left",')]
            + html[html.find(', "visible": false}') + 19 :]
        )
    if clear_memory:
        fig.clear()
        plt.close()
        gc.collect()
    return html


def plot_po(one_survey):
    """Plot a diagram of PO (Porakonekairaus) with matlplotlib.

    Parameters
    ----------
    one_survey : hole object

    Returns
    -------
    axes : list of axes
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
    ax_right.set_ylim(ax_right.get_ylim()[0], 0)

    if soils is not None:
        for _, row in soils.iterrows():
            ax_right.text(0.03, row["Depth (m)"], s=row["Soil type"])

    return fig


def plot_pa(one_survey):
    """Plot a diagram of PA (Painokairaus) with matlplotlib.

    Parameters
    ----------
    one_survey : hole object

    Returns
    -------
    axes : list of axes
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
    ax_right.set_ylim(ax_right.get_ylim()[0], 0)

    return fig


def plot_hole(one_survey, backend="mpld3"):
    """Plot a diagram of PA (Painokairaus) with matplotlib.

    Parameters
    ----------
    one_survey : hole object
    backend : str
        Backend to plot with
        possible values 'mpld3' and 'matplotlib'

    Returns
    -------
    axes : axes
    """
    hole_type = one_survey.header["TT"]["Survey abbreviation"]
    if hole_type == "PO":
        fig = plot_po(one_survey)
        if backend == "matplotlib":
            return fig
        elif backend == "mpld3":
            return fig_to_hmtl(fig)
        else:
            raise NotImplementedError("Plotting backend {} not implemented".format(backend))
    elif hole_type == "PA":
        fig = plot_pa(one_survey)
        if backend == "matplotlib":
            return fig
        elif backend == "mpld3":
            return fig_to_hmtl(fig)
        raise NotImplementedError("Plotting backend {} not implemented".format(backend))
    else:
        raise NotImplementedError('Hole object "{}" not supported'.format(hole_type))
