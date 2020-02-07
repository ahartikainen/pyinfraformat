"""Plot a html folium map from holes object."""
from itertools import cycle
import folium
import branca
from folium.plugins import MarkerCluster
from pyproj import Transformer
import numpy as np

from .holes import plot_hole
from .. import core

ABBREVIATIONS = {
    "CP": "CPT -kairaus",
    "CP/CPT": "CPT -kairaus",
    "CPT": "CPT -kairaus",
    "CPTU": "CPTU -kairaus",
    "CU": "CPTU -kairaus",
    "CU/CPTU": "CPTU -kairaus",
    "FVT": "Siipikairaus",
    "HE": "Heijarikairaus",
    "HE/DP": "Heijarikairaus",
    "HK": "Heijarikairaus vääntömomentilla",
    "HK/DP": "Heijarikairaus vääntömomentilla",
    "HP": "Puristin-heijari -kairaus",
    "KE": "Kallionäytekairaus laajennettu",
    "KO": "Koekuoppa",
    "KR": "Kallionäytekairaus videoitu",
    "LB": "Laboratoriotutkimukset // Kallionäytetutkimus",
    "LY": "Lyöntikairaus",
    "MW": "MWD -kairaus",
    "NE": "Näytteenotto häiriintymätön",
    "NO": "Näytteenotto häiritty",
    "PA": "Painokairaus",
    "PA/WST": "Painokairaus",
    "PI": "Pistokairaus",
    "PMT": "Pressometrikoe",
    "PO": "Porakonekairaus",
    "PR": "Puristinkairaus",
    "PS": "Pressometrikoe",
    "PS/PMT": "Pressometrikoe",
    "PT": "Putkikairaus",
    "RK": "Rakeisuus",
    "SI": "Siipikairaus",
    "SI/FVT": "Siipikairaus",
    "TR": "Tärykairaus",
    "VK": "Vedenpinnan mittaus kaivosta",
    "VO": "Orsiveden mittausputki",
    "VP": "Pohjaveden mittausputki",
    "VPK": "Kalliopohjavesiputki",
    "WST": "Painokairaus",
}


def to_lanlot(x, y, intput_epsg="EPSG:3067"):
    """Transform coordinates to WGS84.

    Parameters
    ----------
    x : list or float
    x : list or float
    intput_epsg : str

    Returns
    -------
    x : list or float
    y : list or float
    """
    transformer = Transformer.from_crs(intput_epsg, "EPSG:4326")
    x, y = transformer.transform(x, y)
    return x, y


def plot_map(holes):
    """Plot a leaflet map from holes with popup hole plots.

    Parameters
    ----------
    holes : holes object

    Returns
    -------
    map_fig : folium map object
    """
    holes_filtered = []
    for hole in holes:
        if hasattr(hole, "header") and hasattr(hole.header, "XY"):
            if "X" in hole.header.XY and "Y" in hole.header.XY:
                holes_filtered.append(hole)
    holes_filtered = core.Holes(holes_filtered)
    x, y = np.mean([(i.header["XY"]["Y"], (i.header["XY"]["X"])) for i in holes_filtered], 0)
    x, y = to_lanlot(x, y)
    map_fig = folium.Map(location=[x, y], zoom_start=14, max_zoom=19, prefer_canvas=True)

    cluster = MarkerCluster(
        control=False,
        options=dict(
            animate=True,
            maxClusterRadius=20,
            showCoverageOnHover=False
            # disableClusteringAtZoom = 18
        ),
    ).add_to(map_fig)
    map_fig.add_child(cluster)
    hole_clusters = {}
    colors = [
        "red",
        "blue",
        "green",
        "purple",
        "orange",
        "darkred",
        "lightred",
        "beige",
        "darkblue",
        "darkgreen",
        "cadetblue",
        "darkpurple",
        "white",
        "pink",
        "lightblue",
        "lightgreen",
        "gray",
        "black",
        "lightgray",
    ]
    colors = cycle(colors)
    clust_colors = {}
    for color, key in zip(colors, holes_filtered.value_counts().keys()):
        hole_clusters[key] = folium.plugins.FeatureGroupSubGroup(
            cluster, name=ABBREVIATIONS[key], show=True
        )
        clust_colors[key] = color
        map_fig.add_child(hole_clusters[key])

    icon = ""
    width = 300
    height = 300
    for i, kairaus in enumerate(holes_filtered):
        y, x = [kairaus.header.XY["X"], kairaus.header.XY["Y"]]
        x, y = to_lanlot(x, y)
        key = kairaus.header["TT"]["Survey abbreviation"]
        try:
            html = plot_hole(kairaus, backend="mpld3")
            iframe = branca.element.IFrame(html=html, width=width, height=height + 20)
            popup = folium.Popup(iframe, max_width=width)
            folium.Marker(
                location=[x, y],
                color="blue",
                popup=popup,
                icon=folium.Icon(color=clust_colors[key], icon=icon),
            ).add_to(hole_clusters[key])

        except NotImplementedError:
            folium.Marker(
                location=[x, y],
                color="red",
                popup=ABBREVIATIONS[key] + " " + str(i),
                icon=folium.Icon(color=clust_colors[key], icon=icon),
            ).add_to(hole_clusters[key])

    folium.LayerControl().add_to(map_fig)
    return map_fig
