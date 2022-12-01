import os
from glob import glob
from uuid import uuid4

import pytest

from pyinfraformat import (
    FileExtensionMissingError,
    Holes,
    PathNotFoundError,
    from_infraformat,
)


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
    hole = holes[0]
    assert len(repr(hole.fileheader)) > 10


def test_iteration():
    holes = get_object()
    for hole in holes:
        assert bool(hole)


def test_subobject_str():
    holes = get_object()
    hole = holes[0]
    assert len(hole.__str__().splitlines()) > 40


def test_subobject_repr():
    holes = get_object()
    hole = holes[0]
    assert len(hole.__repr__().splitlines()) > 40


def test_subobject_pandas():
    holes = get_object()
    hole = holes[0]
    assert hole.dataframe.shape == (6, 53)


def test_object_pandas():
    holes = get_object()
    assert holes.dataframe.shape == (258, 94)
    holes = get_object()
    holes._lowmemory = True
    assert holes._get_dataframe().shape == (258, 94)


def test_drop_duplicates():
    holes = get_object()
    with pytest.raises(NotImplementedError):
        holes.drop_duplicates()


def test_filter_by_date():
    holes = get_object()
    filtered_holes = holes.filter_holes(start="2014-05-18", end="2019-01-10", fmt="%Y-%m-%d")
    assert len(filtered_holes) <= len(holes)

    filtered_holes2 = holes.filter_holes(start="2014-05-18", fmt="%Y-%m-%d")
    filtered_holes3 = filtered_holes2.filter_holes(end="2019-01-10", fmt="%Y-%m-%d")
    assert len(filtered_holes) <= len(filtered_holes3)


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


def test_append_extend_slices():
    holes = get_object()
    holes2 = holes[:-1]
    one_hole = holes[-1]
    assert len(holes2 + one_hole) == len(holes)
    assert len(one_hole + holes2) == len(holes)
    assert len(one_hole + holes[0]) == 2
    holes2.append(one_hole)
    assert len(holes2) == len(holes)

    holes3 = holes[::2]
    holes4 = holes[1::2]
    assert len(holes3 + holes4) == len(holes)
    with pytest.raises(ValueError):
        holes.append("This is not a hole")
    with pytest.raises(ValueError):
        holes.extend("This is a holes".split())
    with pytest.raises(ValueError):
        holes + "This is a holes"
    with pytest.raises(ValueError):
        one_hole + "This is not a hole"
