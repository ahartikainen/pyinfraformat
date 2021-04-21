"""Plot a html folium map from holes object."""
import re
from itertools import cycle
from pathlib import Path

import folium
import numpy as np
from folium.plugins import MarkerCluster, MeasureControl, MousePosition

from ..core import Holes
from ..core.coord_utils import EPSG_SYSTEMS, coord_string_fix, project_points
from .holes import plot_hole

__all__ = ["plot_map"]


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
    "Missing survey abbreviation": "Missing survey abbreviation",
}


def plot_map(holes, render_holes=True, popup_size=(3, 3)):
    """Plot a leaflet map from holes with popup hole plots.

    Parameters
    ----------
    holes : holes object
    render_holes : bool
        Render popup diagrams for holes
    popup_size : tuple
        size in inches of popup figure

    Returns
    -------
    map_fig : folium map object
    """
    holes_filtered = []
    first_system = False
    if len(holes) == 0:
        raise ValueError("Can't plot empty holes -object.")
    for hole in holes:
        if hasattr(hole, "header") and hasattr(hole.header, "XY"):
            if "X" in hole.header.XY and "Y" in hole.header.XY:
                holes_filtered.append(hole)
                coord_system = hole.fileheader.KJ["Coordinate system"]
                coord_system = coord_string_fix(coord_system)
                if re.search(r"^EPSG:\d+$", coord_system, re.IGNORECASE):
                    input_epsg = coord_system
                elif coord_system in EPSG_SYSTEMS:
                    input_epsg = EPSG_SYSTEMS[coord_system]
                else:
                    msg = "Coordinate system {} is not implemented"
                    msg = msg.format(coord_system)
                    raise NotImplementedError(msg)
                if not first_system:
                    first_system = coord_system
                else:
                    if not first_system == coord_system:
                        raise ValueError("Coordinate system is not uniform in holes -object")
    holes_filtered = Holes(holes_filtered)

    x_all, y_all = [], []
    for i in holes_filtered:
        x_all.append(i.header["XY"]["X"])
        y_all.append(i.header["XY"]["Y"])

    x, y = np.mean(x_all), np.mean(y_all)
    x, y = project_points(x, y, input_epsg)
    map_fig = folium.Map(
        location=[x, y], zoom_start=14, max_zoom=20, prefer_canvas=True, control_scale=True
    )
    folium.TileLayer("Stamen Terrain").add_to(map_fig)
    folium.TileLayer("CartoDB positron").add_to(map_fig)
    esri_url = (
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        + "World_Imagery/MapServer/tile/{z}/{y}/{x}"
    )
    folium.TileLayer(
        tiles=esri_url, attr="Esri", name="Esri Satellite", overlay=False, control=True
    ).add_to(map_fig)
    mml_url_perus = "http://tiles.kartat.kapsi.fi/peruskartta/{z}/{x}/{y}.jpg"
    mml_url_orto = "http://tiles.kartat.kapsi.fi/ortokuva/{z}/{x}/{y}.jpg"
    folium.TileLayer(
        tiles=mml_url_perus, attr="MML", name="MML peruskartta", overlay=False, control=True
    ).add_to(map_fig)
    folium.TileLayer(
        tiles=mml_url_orto, attr="MML", name="MML ilmakuva", overlay=False, control=True
    ).add_to(map_fig)

    gtk_url = (
        "http://gtkdata.gtk.fi/arcgis/services/Rajapinnat/GTK_Maapera_WMS/MapServer/WMSServer?"
    )
    folium.WmsTileLayer(
        name="GTK Maaperäkartta",
        url=gtk_url,
        fmt="image/png",
        layers=["maapera_100k_kerrostumat_ja_muodostumat"],  # "maapera_200k_maalajit"
        show=False,
        transparent=True,
        opacity=0.5,
    ).add_to(map_fig)

    folium.WmsTileLayer(
        name="GTK Sulfaattimaat",
        url=gtk_url,
        fmt="image/png",
        layers=["happamat_sulfaattimaat_250k_alueet"],
        show=False,
        transparent=True,
        opacity=0.5,
    ).add_to(map_fig)

    sw_bounds = project_points(min(x_all), min(y_all), input_epsg)
    ne_bounds = project_points(max(x_all), max(y_all), input_epsg)

    map_fig.fit_bounds([sw_bounds, ne_bounds])

    cluster = MarkerCluster(
        control=False,
        options=dict(
            animate=True, maxClusterRadius=20, showCoverageOnHover=False, disableClusteringAtZoom=19
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
        "darkblue",
        "darkgreen",
        "cadetblue",
        "darkpurple",
        "pink",
        "lightblue",
        "lightgreen",
    ]
    colors = cycle(colors)
    clust_icon_kwargs = {}
    for color, key in zip(colors, holes_filtered.value_counts().keys()):
        hole_clusters[key] = folium.plugins.FeatureGroupSubGroup(
            cluster, name=ABBREVIATIONS[key], show=True
        )
        clust_icon_kwargs[key] = dict(color=color, icon="")
        map_fig.add_child(hole_clusters[key])

    for i, hole in enumerate(holes_filtered):
        x, y = [hole.header.XY["X"], hole.header.XY["Y"]]
        x, y = project_points(x, y, input_epsg)

        if hasattr(hole.header, "TT") and "Survey abbreviation" in hole.header["TT"]:
            key = hole.header["TT"]["Survey abbreviation"]
        else:
            key = "Missing survey abbreviation"
        if render_holes and key != "Missing survey abbreviation":
            try:
                hole_svg = plot_hole(hole, output="svg", figsize=popup_size)
                popup = folium.Popup(hole_svg)
                icon = get_icon(key, clust_icon_kwargs)
                folium.Marker(location=[x, y], popup=popup, icon=icon).add_to(hole_clusters[key])

            except (NotImplementedError, KeyError):
                icon = get_icon(key, clust_icon_kwargs)
                folium.Marker(
                    location=[x, y],
                    popup=ABBREVIATIONS[key] + " " + str(i),
                    icon=icon,
                ).add_to(hole_clusters[key])
        else:
            icon = get_icon(key, clust_icon_kwargs)
            folium.Marker(
                location=[x, y],
                popup=ABBREVIATIONS[key] + " " + str(i),
                icon=icon,
            ).add_to(hole_clusters[key])

    folium.LayerControl().add_to(map_fig)
    MeasureControl(
        secondary_length_unit="",
        secondary_area_unit="",
        activeColor="#aecfeb",
        completedColor="#73b9f5",
    ).add_to(map_fig)
    fmtr = "function(num) {return L.Util.formatNum(num, 7) + ' º ';};"
    MousePosition(
        position="topright",
        separator=" | ",
        prefix="WGS84 ",
        lat_formatter=fmtr,
        lng_formatter=fmtr,
    ).add_to(map_fig)
    return map_fig


def get_icon(abbreviation, clust_icon_kwargs, default=False):
    """Get icon from /icons or create colored default folium icon."""
    if default:
        return folium.Icon(**clust_icon_kwargs[abbreviation])
    path = Path(__file__).parent

    icon_path = "icons//{abb}.svg".format(abb=abbreviation.replace("//", "_"))
    # print(path/icon_path, path)
    # print(abbreviation)
    try:
        with open(path / icon_path, "r") as f:
            svg_str = f.read()
    except FileNotFoundError:
        return folium.Icon(**clust_icon_kwargs[abbreviation])
    height = float(
        [line for line in svg_str.split() if line.startswith("height")][0]
        .split("=")[-1]
        .replace('"', "")
    )
    width = float(
        [line for line in svg_str.split() if line.startswith("width")][0]
        .split("=")[-1]
        .replace('"', "")
    )
    icon = folium.DivIcon(html=svg_str, icon_anchor=(width / 2, height / 2))
    return icon
