from glob import glob
import os
import pyinfraformat as pif
import pytest

def get_datafiles():
    here = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(here, "data", "*.tek")
    datafiles = glob(data_directory)
    if len(datafiles):
        return datafiles
    else:
        raise FileNotFound(f"Missing test data: {data_directory}")


def test_reading_good():
    for path in get_datafiles():
        if "_bad_" not in path:
            holes = pif.from_infraformat(path)
            assert str(type(holes))  == "<class 'pyinfraformat.core.Holes'>"
            assert isinstance(holes.holes, list)


def test_reading_bad():
    #skip
    return
    for path in get_datafiles():
        if "_bad_" in path:
            with pytest.raises(Exception):
                pif.from_infraformat(path)


def test_reading_empty():
    holes = pif.from_infraformat()
    assert str(type(holes)) == "<class 'pyinfraformat.core.Holes'>"
    holes = pif.from_infraformat([])
    assert str(type(holes)) == "<class 'pyinfraformat.core.Holes'>"

def test_output():
    for path in get_datafiles():
        if "_bad_" not in path:
            holes = pif.from_infraformat(path)
            assert str(type(holes))  == "<class 'pyinfraformat.core.Holes'>"
            if len(holes.holes) > 0:
                here = os.path.dirname(os.path.abspath(__file__))
                output_path = os.path.join(here, "data", "test_output.csv")
                holes.to_csv(output_path)
