"""Plot a html folium map from holes object"""

import folium
import branca
from folium.plugins import MarkerCluster
from pyproj import Transformer
import numpy as np

from .holes import plot_pa, plot_po

abbreviations = {
    "PA": "Painokairaus",
    "PI": "Pistokairaus",
    "LY": "Lyöntikairaus",
    "SI": "Siipikairaus",
    "HE": "Heijarikairaus",
    "PT": "Putkikairaus",
    "TR": "Tärykairaus",
    "PR": "Puristinkairaus",
    "CP": "CPT -kairaus",
    "CU": "CPTU -kairaus",
    "HP": "Puristin-heijari -kairaus",
    "PO": "Porakonekairaus",
    "VP": "Pohjaveden mittausputki",
    "VO": "Orsiveden mittausputki",
    "KO": "Koekuoppa",
    "NO": "Näytteenotto häiritty",
    "NE": "Näytteenotto häiriintymätön",
}


def to_lanlot(x, y):
    """ETRS-TM35FIN to WGS84"""
    transformer = Transformer.from_crs("EPSG:3067", "EPSG:4326")
    x, y = transformer.transform(x, y)
    return x, y


def plot_map(holes):
    """Plot a leaflet map from holes with popup hole plots

    Parameters
    ----------
    holes : holes object

    Returns
    -------
    map_fig : folium map object
    """
    x, y = np.mean([(i.header["XY"]["Y"], (i.header["XY"]["X"])) for i in holes], 0)
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

    pa_cluster = folium.plugins.FeatureGroupSubGroup(cluster, name="Painokairaus", show=True)
    po_cluster = folium.plugins.FeatureGroupSubGroup(cluster, name="Porakonekairaukset", show=True)
    lo_cluster = folium.plugins.FeatureGroupSubGroup(cluster, name="Muut kairaukset", show=False)

    map_fig.add_child(cluster)
    map_fig.add_child(pa_cluster)
    map_fig.add_child(po_cluster)
    map_fig.add_child(lo_cluster)

    icon = ""
    for i, kairaus in enumerate(holes):
        y, x = [kairaus.header.XY["X"], kairaus.header.XY["Y"]]
        x, y = to_lanlot(x, y)
        tyyppi = kairaus.header["TT"]["Survey abbreviation"]
        if tyyppi == "PA":
            html = plot_pa(kairaus, "html")
            iframe = branca.element.IFrame(html=html, width=300, height=320)
            popup = folium.Popup(iframe, max_width=300)
            folium.Marker(
                location=[x, y],
                color="blue",
                popup=popup,
                icon=folium.Icon(color="blue", icon=icon),
            ).add_to(pa_cluster)
        elif tyyppi == "PO":
            html = plot_po(kairaus, "html")
            iframe = branca.element.IFrame(html=html, width=300, height=320)
            popup = folium.Popup(iframe, max_width=300)
            folium.Marker(
                location=[x, y], color="red", popup=popup, icon=folium.Icon(color="red", icon=icon)
            ).add_to(po_cluster)

        else:
            folium.Marker(
                location=[x, y],
                color="red",
                popup=abbreviations[tyyppi] + " " + str(i),
                icon=folium.Icon(color="orange", icon=icon),
            ).add_to(lo_cluster)

    folium.LayerControl().add_to(map_fig)
    return map_fig
