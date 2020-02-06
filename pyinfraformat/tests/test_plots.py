from glob import glob
import os
from uuid import uuid4
from pyinfraformat import plot_map
import folium
import pytest


def get_object():
    here = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(here, "test_data", "infraformat_hole_types.tek")
    object = from_infraformat(filepath)
    return object


def test_map():
    holes = get_object()
    holes_map = plot_map(holes)
    assert isinstance(holes_map, folium.Map)
