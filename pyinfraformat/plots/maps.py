"""Plot a html folium map from holes object."""
from itertools import cycle
import folium
import branca
from folium.plugins import MarkerCluster, MeasureControl, MousePosition
import numpy as np

from .holes import plot_hole
from ..core import Holes
from ..core.coord_utils import to_lanlot, get_epsg_systems, coord_string_fix

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
}


def plot_map(holes, render_holes=True):
    """Plot a leaflet map from holes with popup hole plots.

    Parameters
    ----------
    holes : holes object
    render_holes : bool
        Render popup diagrams for holes

    Returns
    -------
    map_fig : folium map object
    """
    holes_filtered = []
    first_system = False
    for hole in holes:
        if hasattr(hole, "header") and hasattr(hole.header, "XY"):
            if "X" in hole.header.XY and "Y" in hole.header.XY:
                holes_filtered.append(hole)
                coord_system = hole.fileheader.KJ["Coordinate system"]
                coord_system = coord_string_fix(coord_system)
                epsg_systems = get_epsg_systems()
                if coord_system in epsg_systems:
                    input_epsg = epsg_systems[coord_system][0]
                else:
                    msg = "Coordinate system {} not implemted"
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
    x, y = to_lanlot(x, y, input_epsg)
    map_fig = folium.Map(
        location=[x, y], zoom_start=14, max_zoom=19, prefer_canvas=True, control_scale=True
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
    sw_bounds = to_lanlot(min(x_all), min(y_all), input_epsg)
    ne_bounds = to_lanlot(max(x_all), max(y_all), input_epsg)
    map_fig.fit_bounds([sw_bounds, ne_bounds])

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

    width = 300
    height = 300
    for i, hole in enumerate(holes_filtered):
        x, y = [hole.header.XY["X"], hole.header.XY["Y"]]
        x, y = to_lanlot(x, y, input_epsg)
        key = hole.header["TT"]["Survey abbreviation"]
        if render_holes:
            try:
                html = plot_hole(hole, backend="mpld3")
                iframe = branca.element.IFrame(html=html, width=width, height=height + 5)
                popup = folium.Popup(iframe, max_width=width)
                folium.Marker(
                    location=[x, y], popup=popup, icon=folium.Icon(**clust_icon_kwargs[key])
                ).add_to(hole_clusters[key])

            except (NotImplementedError, KeyError):
                folium.Marker(
                    location=[x, y],
                    popup=ABBREVIATIONS[key] + " " + str(i),
                    icon=folium.Icon(**clust_icon_kwargs[key]),
                ).add_to(hole_clusters[key])
        else:
            folium.Marker(
                location=[x, y],
                popup=ABBREVIATIONS[key] + " " + str(i),
                icon=folium.Icon(**clust_icon_kwargs[key]),
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
