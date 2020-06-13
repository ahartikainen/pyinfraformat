import os
from glob import glob
from uuid import uuid4

import pytest

import folium
from pyinfraformat import from_infraformat, plot_map


def get_object():
    here = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(here, "test_data", "infraformat_hole_types.tek")
    object = from_infraformat(filepath)
    return object


def test_map():
    holes = get_object()
    holes_map = plot_map(holes)
    assert isinstance(holes_map, folium.Map)
