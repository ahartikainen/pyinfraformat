import os
from glob import glob
from uuid import uuid4

import pytest

import folium
import matplotlib.pyplot as plt
from pyinfraformat import from_infraformat, from_gtk_wfs, plot_map


def get_object():
    here = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(here, "test_data", "infraformat_hole_types.tek")
    object = from_infraformat(filepath)
    return object

def test_holes_plot():
    holes = get_object()
    for hole in holes:
        try:
            fig = hole.plot()
            assert isinstance(fig, plt.Figure)
        except NotImplementedError:
            pass

def test_map():
    holes = get_object()
    holes_map = plot_map(holes)
    assert isinstance(holes_map, folium.Map)


def test_gtk_map():
    holes = get_object()
    holes_map = plot_map(holes)
    bbox = (60.12065, 24.4421945, 60.1208, 24.443)  # Bbox with empty and missing data holes
    holes = from_gtk_wfs(bbox, "WGS84")
    holes_map = plot_map(holes)
    assert isinstance(holes_map, folium.Map)
