from glob import glob
import os
from uuid import uuid4
from pyinfraformat import from_infraformat, Holes, FileExtensionMissingError, PathNotFoundError
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
        holes = from_infraformat(path, robust=robust)
        assert isinstance(holes, Holes)
        assert isinstance(holes.holes, list)


@pytest.mark.xfail(reason="read invalid data")
def test_reading_bad():
    for path in get_datafiles("bad"):
        with pytest.raises(Exception):
            from_infraformat(path)
    with pytest.raises(Exception):
        from_infraformat("../ImaginaryFolder")


def test_reading_empty():
    holes = from_infraformat()
    assert isinstance(holes, Holes)
    holes = from_infraformat([])
    assert isinstance(holes, Holes)
    holes = from_infraformat("")
    assert isinstance(holes, Holes)


def test_output():
    for path in get_datafiles("good"):
        holes = from_infraformat(path)
        assert isinstance(holes, Holes)
        if len(holes.holes) > 0:
            here = os.path.dirname(os.path.abspath(__file__))
            output_path = os.path.join(here, "test_data", str(uuid4()) + "_output_example.csv")
            assert not os.path.exists(output_path)
            holes.to_csv(output_path)
            assert os.path.exists(output_path)
            os.remove(output_path)
            assert not os.path.exists(output_path)

            output_path = os.path.join(here, "test_data", str(uuid4()) + "_output_example")
            with pytest.raises(FileExtensionMissingError):
                holes.to_csv(output_path)

            output_path = os.path.join(here, "test_data", str(uuid4()) + "_output_example.csv")
            assert not os.path.exists(output_path)
            holes.to_excel(output_path)
            assert os.path.exists(output_path)
            os.remove(output_path)
            assert not os.path.exists(output_path)

            output_path = os.path.join(here, "test_data", str(uuid4()) + "_output_example")
            with pytest.raises(FileExtensionMissingError):
                holes.to_excel(output_path)

            output_path = os.path.join(here, "test_data", str(uuid4()) + "_output_example.tek")
            assert not os.path.exists(output_path)
            holes.to_infraformat(output_path)
            assert os.path.exists(output_path)
            os.remove(output_path)
            assert not os.path.exists(output_path)
