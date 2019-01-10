from glob import glob
import os
import pyinfraformat as pif
import pytest


def get_datafiles():
    here = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(here, "test_data", "*.tek")
    datafiles = glob(data_directory)
    return datafiles


def test_reading_good():
    for path in get_datafiles():
        if "_bad_" not in path:
            holes = pif.from_infraformat(path)
            assert str(type(holes)) == "<class 'pyinfraformat.core.Holes'>"
            assert isinstance(holes.holes, list)


@pytest.mark.xfail(reason="read invalid data")
def test_reading_bad():
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
            assert str(type(holes)) == "<class 'pyinfraformat.core.Holes'>"
            if len(holes.holes) > 0:
                here = os.path.dirname(os.path.abspath(__file__))
                output_path = os.path.join(here, "test_data", "test_output.csv")
                if os.path.exists(output_path):
                    os.remove(output_path)
                assert not os.path.exists(output_path)
                holes.to_csv(output_path)
                assert os.path.exists(output_path)
                os.remove(output_path)
                assert not os.path.exists(output_path)
