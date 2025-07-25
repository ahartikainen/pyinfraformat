"""Plot a html folium map from holes object."""

from itertools import cycle
from pathlib import Path

import folium
import numpy as np
from folium.plugins import MarkerCluster, MeasureControl, MousePosition
from tqdm.autonotebook import tqdm

from pyinfraformat.core import Holes
from pyinfraformat.core.coord_utils import coord_str_recognize, project_points
from pyinfraformat.core.utils import ABBREVIATIONS

from .holes import plot_hole

__all__ = ["plot_map"]


def plot_map(holes, render_holes=True, progress_bar=True, popup_size=(3, 3)):
    """
    Plot a leaflet map from holes with popup hole plots.

    Parameters
    ----------
    holes : holes object
    render_holes : bool
        Render popup diagrams for holes
    progress_bar : bool
        Show tqdm progress bar while adding/rendering holes
    popup_size : tuple
        size in inches of popup figure

    Returns
    -------
    map_fig : folium map object

    """
    holes_filtered = []
    first_system = False
    if len(holes) == 0:
        msg = "Can't plot empty holes -object."
        raise ValueError(msg)
    for hole in holes:
        if hasattr(hole, "header") and hasattr(hole.header, "XY"):
            if "X" in hole.header.XY and "Y" in hole.header.XY:
                holes_filtered.append(hole)
                coord_system = hole.fileheader.KJ["Coordinate system"]
                input_epsg = coord_str_recognize(coord_system)
                if "unknown" in input_epsg.lower():
                    msg = "Coordinate system {} is unrecognized format / unknown name"
                    msg = msg.format(coord_system)
                    raise ValueError(msg)
                if not first_system:
                    first_system = coord_system
                elif first_system != coord_system:
                    msg = "Coordinate system is not uniform in holes -object"
                    raise ValueError(msg)
    holes_filtered = Holes(holes_filtered)

    x_all, y_all = [], []
    for i in holes_filtered:
        x_all.append(i.header["XY"]["X"])
        y_all.append(i.header["XY"]["Y"])

    x, y = np.mean(x_all), np.mean(y_all)
    x, y = project_points(x, y, input_epsg)
    max_zoom = 22
    map_fig = folium.Map(
        location=[x, y],
        zoom_start=14,
        max_zoom=22,
        prefer_canvas=True,
        control_scale=True,
        tiles=None,
    )
    folium.TileLayer("OpenStreetMap", maxNativeZoom=19, maxZoom=max_zoom).add_to(map_fig)
    folium.TileLayer("CartoDB positron", maxNativeZoom=18, maxZoom=max_zoom).add_to(map_fig)
    esri_url = (
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/{z}/{y}/{x}"
    )
    folium.TileLayer(
        tiles=esri_url,
        attr="Esri",
        name="Esri Satellite",
        overlay=False,
        control=True,
        maxNativeZoom=18,
        maxZoom=max_zoom,
    ).add_to(map_fig)
    mml_url_perus = "http://tiles.kartat.kapsi.fi/peruskartta/{z}/{x}/{y}.jpg"
    mml_url_orto = "http://tiles.kartat.kapsi.fi/ortokuva/{z}/{x}/{y}.jpg"
    folium.TileLayer(
        tiles=mml_url_perus,
        attr="MML",
        name="MML peruskartta",
        overlay=False,
        control=True,
        maxNativeZoom=18,
        maxZoom=max_zoom,
    ).add_to(map_fig)
    folium.TileLayer(
        tiles=mml_url_orto,
        attr="MML",
        name="MML ilmakuva",
        overlay=False,
        control=True,
        maxNativeZoom=18,
        maxZoom=max_zoom,
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
        options={
            "animate": True,
            "maxClusterRadius": 15,
            "showCoverageOnHover": False,
            "disableClusteringAtZoom": 20,
        },
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
    for color, key in zip(colors, holes_filtered.value_counts().keys(), strict=False):
        hole_clusters[key] = folium.plugins.FeatureGroupSubGroup(
            cluster, name=ABBREVIATIONS.get(key, "Unrecognize abbreviation"), show=True
        )
        clust_icon_kwargs[key] = {"color": color, "icon": ""}
        map_fig.add_child(hole_clusters[key])

    if progress_bar:
        pbar = tqdm(
            total=len(holes_filtered),
            desc="Rendering holes" if render_holes else "Adding points to map",
        )
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

            except (NotImplementedError, KeyError, TypeError):
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
                popup=ABBREVIATIONS.get(key, f"Unrecognize abbreviation {key}") + " " + str(i),
                icon=icon,
            ).add_to(hole_clusters[key])

        if progress_bar:
            pbar.update(1)

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
        with open(path / icon_path, encoding="utf-8") as f:
            svg_str = f.read()
    except FileNotFoundError:
        return folium.Icon(**clust_icon_kwargs[abbreviation])
    height = float(
        next(line for line in svg_str.split() if line.startswith("height"))
        .split("=")[-1]
        .replace('"', "")
    )
    width = float(
        next(line for line in svg_str.split() if line.startswith("width"))
        .split("=")[-1]
        .replace('"', "")
    )
    return folium.DivIcon(html=svg_str, icon_anchor=(width / 2, height / 2))
