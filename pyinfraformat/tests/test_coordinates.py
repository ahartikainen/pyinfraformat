from glob import glob
import os
from uuid import uuid4
from pyinfraformat import from_infraformat, Holes
from pyinfraformat.core.coord_utils import coord_string_fix, change_x_to_y, project_holes
import pytest


def get_object():
    here = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(here, "test_data", "infraformat_hole_types.tek")
    object = from_infraformat(filepath)
    return object


def test_fix_coord_str():
    s = {
        "GK25": "ETRS-GK25",
        "GK26": "ETRS-GK26",
        "WGS84": "WGS84",
        "ETRS GK26": "ETRS-GK26",
        "ETRS_GK26": "ETRS-GK26",
    }
    for i in s:
        assert coord_string_fix(i) == s[i]


def test_coordinate_projection_uniform():
    holes = get_object()
    holes = project_holes(holes)
    l = [hole.fileheader.KJ["Coordinate system"] for hole in holes]
    assert all([l[0] == i for i in l])


def test_coordinate_projection():
    holes = get_object()
    holes = change_x_to_y(holes)
    holes2 = project_holes(holes, output_epsg="EPSG:4326", check="Finland")
    holes3 = project_holes(holes, output_epsg="EPSG:3879", check="Finland")
    assert check_area(holes2, epsg="EPSG:4326", country="FI") == True
    assert check_area(holes3, epsg="EPSG:3879", country="EE") == False
