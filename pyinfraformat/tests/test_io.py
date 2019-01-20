from glob import glob
import os
from uuid import uuid4
import pyinfraformat as pif
import pytest


def get_datafiles(quality=None):
    here = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(here, "test_data", "*.tek")
    datafiles = glob(data_directory)
    if isinstance(quality, str) and quality.lower() == "bad":
        # use regex here
        datafiles = [path for path in datafiles if "_bad" in path]
    elif isinstance(quality, str) and quality.lower() == "good":
        # use regex here
        datafiles = [path for path in datafiles if "_bad" not in path]
    return datafiles


@pytest.mark.parametrize("robust", [True, False])
def test_reading_good(robust):
    for path in get_datafiles("good"):
        holes = pif.from_infraformat(path, robust=robust)
        assert isinstance(holes, pif.Holes)
        assert isinstance(holes.holes, list)


@pytest.mark.xfail(reason="read invalid data")
def test_reading_bad():
    for path in get_datafiles("bad"):
        with pytest.raises(Exception):
            pif.from_infraformat(path)


def test_reading_empty():
    holes = pif.from_infraformat()
    assert isinstance(holes, pif.Holes)
    holes = pif.from_infraformat([])
    assert isinstance(holes, pif.Holes)
    holes = pif.from_infraformat("")
    assert isinstance(holes, pif.Holes)
    holes = pif.from_infraformat("../tests")
    assert isinstance(holes, pif.Holes)


def test_output():
    for path in get_datafiles("good"):
        holes = pif.from_infraformat(path)
        assert isinstance(holes, pif.Holes)
        if len(holes.holes) > 0:
            here = os.path.dirname(os.path.abspath(__file__))
            output_path = os.path.join(here, "test_data", str(uuid4()) + "_output_example.csv")
            assert not os.path.exists(output_path)
            holes.to_csv(output_path)
            assert os.path.exists(output_path)
            os.remove(output_path)
            assert not os.path.exists(output_path)
