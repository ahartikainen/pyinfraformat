"""Plots for single hole
different plots for each hole type
"""
import pandas as pd
import matplotlib.pyplot as plt
import mpld3


def plot_po(one_survey, return_value="fig"):
    """Plot a PO, Porakonekairaus
    returns a mpld3 html or matplotlib fig"""
    df = pd.DataFrame(one_survey.survey.data)
    if "Soil type" in df.columns:  # pylint: disable=unsupported-membership-test
        soils = df.dropna(subset=["Soil type"])
    else:
        soils = None
    df = pd.concat((df, df)).sort_values(by=["Depth (m)", "linenumber"])
    df["Depth (m)"] = df["Depth (m)"].shift(1)

    fig, (left, right) = plt.subplots(
        1, 2, sharey=True, gridspec_kw={"wspace": 0, "width_ratios": [2, 2]}
    )
    fig.set_figwidth(4)
    left.plot(df["Time (s)"], df["Depth (m)"], c="k")
    left.invert_yaxis()
    left.spines["top"].set_visible(False)
    left.spines["left"].set_visible(False)
    left.get_yaxis().set_visible(False)
    left.set_xlim([110, 0])
    plt.setp(left.get_yticklabels(), visible=False)

    right.yaxis.set_tick_params(which="both", labelbottom=True)
    right.spines["top"].set_visible(False)
    right.spines["right"].set_visible(False)
    right.spines["bottom"].set_visible(False)
    right.set_xticks([])
    right.set_title(one_survey.header.date.isoformat().split("T")[0])
    left.set_title("{:+.2f}".format(float(one_survey.header["XY"]["Z-start"])))
    right.set_ylim(right.get_ylim()[0], 0)

    if soils is not None:
        for _, row in soils.iterrows():
            right.text(0.03, row["Depth (m)"], s=row["Soil type"])

    if return_value == "fig":
        return fig.axes
    if return_value == "html":
        html = mpld3.fig_to_html(fig, no_extras=True, template_type="simple")
        html = (
            html[0 : html.find(', {"position": "left",')]
            + html[html.find(', "visible": false}') + 19 :]
        )
        fig.clear()
        plt.close()
        return html
    else:
        raise ValueError("return_value invalid")


def plot_pa(one_survey, return_value="fig"):
    """Plot a PA, Painokairaus
    returns a mpld3 html or matplotlib fig"""
    df = pd.DataFrame(one_survey.survey.data)
    df = pd.concat((df, df)).sort_values(by=["Depth (m)", "linenumber"])
    df["Depth (m)"] = df["Depth (m)"].shift(1)
    # df["Load (kN)"][df["Load (kN)"]>=100] = 0
    df.loc[df["Load (kN)"] >= 100, "Load (kN)"] = 0

    fig, (left, right) = plt.subplots(
        1, 2, sharey=True, gridspec_kw={"wspace": 0, "width_ratios": [1, 3]}
    )
    fig.set_figwidth(4)
    left.plot(df["Load (kN)"], df["Depth (m)"], c="k")
    left.invert_yaxis()
    left.spines["top"].set_visible(False)
    left.spines["left"].set_visible(False)
    left.get_yaxis().set_visible(False)

    plt.setp(left.get_yticklabels(), visible=False)

    left.set_xlim([100, 0])
    right.plot(df["Rotation of half turns (-)"], df["Depth (m)"], c="k")
    right.yaxis.set_tick_params(which="both", labelbottom=True)
    right.spines["top"].set_visible(False)
    right.spines["right"].set_visible(False)
    right.set_xlim([0, 110])
    right.set_title(one_survey.header.date.isoformat().split("T")[0])
    left.set_title("{:+.2f}".format(float(one_survey.header["XY"]["Z-start"])))
    right.set_ylim(right.get_ylim()[0], 0)

    if return_value == "fig":
        return fig.axes
    if return_value == "html":
        html = mpld3.fig_to_html(fig, no_extras=True, template_type="simple")
        html = (
            html[0 : html.find(', {"position": "left",')]
            + html[html.find(', "visible": false}') + 19 :]
        )
        fig.clear()
        plt.close()
        return html
    else:
        raise ValueError("return_value invalid")


def plot_hole(one_survey, return_value="fig"):
    """Plot hole object"""
    hole_type = one_survey.header["TT"]["Survey abbreviation"]
    if hole_type == "PO":
        return plot_po(one_survey, return_value=return_value)
    if hole_type == "PA":
        return plot_pa(one_survey, return_value=return_value)
    else:
        raise NotImplementedError
