import os
from glob import glob
from io import BytesIO, StringIO
from uuid import uuid4

import pytest

import pyinfraformat as pif
from pyinfraformat import (
    FileExtensionMissingError,
    Holes,
    PathNotFoundError,
    from_gtk_wfs,
    from_infraformat,
)

from .helpers import ping_gtk


def get_datafiles(quality=None, encoding=None):
    here = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(here, "test_data", "*.tek")
    datafiles = glob(data_directory)
    if isinstance(quality, str) and quality.lower() == "bad":
        # use regex here
        datafiles = [path for path in datafiles if "_bad" in path]
    elif isinstance(quality, str) and quality.lower() == "good":
        # use regex here
        datafiles = [path for path in datafiles if "_bad" not in path]

    if isinstance(encoding, str) and encoding.lower() == "utf-16":
        datafiles = [path for path in datafiles if "utf16" in path]
    elif isinstance(encoding, str) and encoding.lower() == "ascii":
        datafiles = [path for path in datafiles if "utf16" not in path]
    return datafiles


@pytest.mark.parametrize("errors", ["raise", "ignore_lines", "ignore_holes"])
def test_reading_good(errors):
    for path in get_datafiles("good"):
        holes = from_infraformat(path, errors=errors)
        assert isinstance(holes, Holes)
        assert isinstance(holes.holes, list)


@pytest.mark.parametrize("errors", ["raise", "ignore_lines", "ignore_holes", "force"])
@pytest.mark.parametrize("encoding", ["utf-16", "auto"])
def test_reading_good_encoding(errors, encoding):
    for path in get_datafiles("good", "utf-16"):
        holes = from_infraformat(path, errors=errors, encoding=encoding)
        assert isinstance(holes, Holes)
        assert isinstance(holes.holes, list)


@pytest.mark.parametrize("errors", ["raise", "ignore_lines", "ignore_holes", "force"])
def test_reading_good_stringio(errors):
    for path in get_datafiles("good", "ascii"):
        with StringIO() as text:
            with open(path, "r") as f:
                text.write(f.read())
            text.seek(0)
            holes = from_infraformat(text, errors=errors)

        assert isinstance(holes, Holes)
        assert isinstance(holes.holes, list)


@pytest.mark.parametrize("errors", ["raise", "ignore_lines", "ignore_holes", "force"])
def test_reading_good_bytesio(errors):
    for path in get_datafiles("good"):
        with BytesIO() as text:
            with open(path, "rb") as f:
                text.write(f.read())
            text.seek(0)
            holes = from_infraformat(text, errors=errors)

        assert isinstance(holes, Holes)
        assert isinstance(holes.holes, list)


def test_reading_bad():
    for path in get_datafiles("bad"):
        with pytest.raises(Exception):
            from_infraformat(path, errors="raise")
    with pytest.raises(Exception):
        from_infraformat("../ImaginaryFolder")


@pytest.mark.parametrize("encoding", ["utf-8", "ascii"])
def test_reading_bad_encoding(encoding):
    for path in get_datafiles(None, "utf-16"):
        with pytest.raises(UnicodeDecodeError):
            from_infraformat(path, errors="raise", encoding=encoding)


def test_reading_bad_stringio():
    for path in get_datafiles("bad"):
        with StringIO() as text:
            with open(path, "r") as f:
                text.write(f.read())
            text.seek(0)
            with pytest.raises(Exception):
                from_infraformat(text, errors="raise")


def test_reading_bad_bytesio():
    for path in get_datafiles("bad"):
        with BytesIO() as text:
            with open(path, "rb") as f:
                text.write(f.read())
            text.seek(0)
            with pytest.raises(Exception):
                from_infraformat(text, errors="raise")


def test_reading_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(here, "test_data")
    paths_read = []
    try:
        path_read = from_infraformat(data_directory)
    except:
        # this just tests that one of the files is read correctly.
        pass

    path_read = from_infraformat(data_directory, extension=".tek2")
    path_read = from_infraformat(data_directory, extension="tek2")


def test_reading_empty():
    holes = from_infraformat()
    assert isinstance(holes, Holes)
    holes = from_infraformat([])
    assert isinstance(holes, Holes)
    holes = from_infraformat("")
    assert isinstance(holes, Holes)


@pytest.mark.skipif(not ping_gtk(), reason="GTK DB not available")
def test_gtk_wfs():
    bbox = (60.2, 24.8, 60.215, 24.83)
    holes = from_gtk_wfs(bbox, "EPSG:4326", progress_bar=True)
    assert len(Holes(holes[:3]).get_dataframe()) > 0
    assert len(holes[0].get_dataframe()) > 0
    assert isinstance(holes, Holes)
    df_endings = holes.get_endings(False)
    assert len(df_endings) > 0

    bbox = [6686269, 392073, 6686279, 392083]
    holes = from_gtk_wfs(bbox, "TM35fin", progress_bar=True)  # malformated json
    assert len(holes) == 3


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

            output_path = os.path.join(here, "test_data", str(uuid4()) + "_output_example.xlsx")
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

            with StringIO() as output_io:
                output_io.seek(0)
                holes.to_infraformat(output_io)
                output_io.seek(0)
                assert len(output_io.read())


def test_set_logger():
    pif.set_logger_level(10)
    pif.log_to_file("test_log.log")
    for path in get_datafiles("good"):
        holes = from_infraformat(path)
    with open("test_log.log") as f:
        length = len(f.read())
    assert length > 0
