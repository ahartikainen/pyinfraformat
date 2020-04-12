from glob import glob
import os
from uuid import uuid4
from pyinfraformat import from_infraformat, Holes, FileExtensionMissingError, PathNotFoundError
from pyinfraformat import project_holes
import pytest


def get_object():
    here = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(here, "test_data", "infraformat_hole_types.tek")
    object = from_infraformat(filepath)
    return object


def test_str():
    holes = get_object()
    assert len(holes.__str__().splitlines()) == 40


def test_repr():
    holes = get_object()
    assert len(holes.__repr__().splitlines()) == 40


def test_iteration():
    holes = get_object()
    for hole in holes:
        assert bool(hole)


def test_subobject_str():
    holes = get_object()
    hole = holes[0]
    assert len(hole.__str__().splitlines()) == 54


def test_subobject_repr():
    holes = get_object()
    hole = holes[0]
    assert len(hole.__repr__().splitlines()) == 54


def test_subobject_pandas():
    holes = get_object()
    hole = holes[0]
    assert hole.dataframe.shape == (6, 53)


def test_object_pandas():
    holes = get_object()
    assert holes.dataframe.shape == (258, 95)


def test_drop_duplicates():
    holes = get_object()
    with pytest.raises(NotImplementedError):
        holes.drop_duplicates()


def test_filter_by_date():
    holes = get_object()
    filtered_holes = holes.filter_holes(start="2014-05-18", end="2019-01-10", fmt="%Y-%m-%d")
    assert len(filtered_holes) <= len(holes)


def test_filter_by_hole_type():
    holes = get_object()
    filtered_holes = holes.filter_holes(hole_type=["PO"])
    filtered_holes2 = holes.filter_holes(hole_type="PO")
    assert len(filtered_holes) == len(filtered_holes2)
    assert len(filtered_holes) <= len(holes)


def test_filter_by_coordinates():
    holes = get_object()
    filtered_holes = holes.filter_holes(bbox=(24, 25, 60, 61))
    assert len(filtered_holes) <= len(holes)
