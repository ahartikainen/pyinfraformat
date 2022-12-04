import os
from copy import deepcopy
from glob import glob
from uuid import uuid4

import numpy as np
import pytest

from pyinfraformat import Holes, from_infraformat
from pyinfraformat.core.coord_utils import (
    check_hole_in_country,
    coord_str_recognize,
    flip_xy,
    height_systems_diff,
    proj_espoo,
    proj_helsinki,
    proj_porvoo,
    project_hole,
    project_holes,
    project_points,
)


def get_object():
    here = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(here, "test_data", "infraformat_hole_types.tek")
    object = from_infraformat(filepath)
    return object


@pytest.mark.parametrize(
    "strings",
    [("WGS84", "WGS 84"), ("Gk25", "ETRS89 / GK25FIN"), ("TM35FIN", "ETRS89 / TM35FIN(E,N)")],
)
def test_fix_coord_str(strings):
    intput_str, correct = strings
    output_str = coord_str_recognize(intput_str)
    assert output_str == correct


def test_holes_projection_uniform():
    holes = get_object()
    holes = project_holes(holes)
    l = [hole.fileheader.KJ["Coordinate system"] for hole in holes]
    assert all([l[0] == i for i in l])


def test_holes_coordinate_projection():
    holes = get_object()
    holes = flip_xy(holes)
    holes = flip_xy(holes)
    hole = holes[0]
    hole = flip_xy(hole)
    hole = flip_xy(hole)
    holes2 = project_holes(holes, output="EPSG:4326", check="Finland")
    holes3 = project_holes(holes, output="EPSG:3879", check="Finland")
    holes4 = project_holes(holes, output="EPSG:4326", check="Estonia")  # logger warning
    holes5 = holes.project("ykj")
    hole = project_holes(holes[0], output="EPSG:3879", check="Finland")
    hole = project_holes(hole, output="EPSG:3879", check="Finland")
    assert check_hole_in_country(holes2, country="FI")
    assert check_hole_in_country(holes3, country="FI")
    assert check_hole_in_country(holes3, country="EE") == False


def test_hole_coordinate_projection():
    holes = get_object()
    hole = holes[5]
    hole.header.XY["X"] = 28837.457
    hole.header.XY["Y"] = 47640.142
    hole.fileheader.KJ["Coordinate system"] = "Helsinki"
    hole = project_hole(hole, output_epsg="EPSG:3879")
    assert check_hole_in_country(hole, country="FI")


def test_holes_projection_errors():
    holes = get_object()
    with pytest.raises(Exception) as e_info:
        project_holes("Wrong input")
    assert str(e_info.value) == "holes -parameter is unknown input type"

    with pytest.raises(Exception) as e_info:
        project_hole(holes[0], output_epsg="EPSG:999999")
    assert "Internal Proj Error" in str(e_info.value)

    hole = holes[0]
    hole.header.XY["X"], hole.header.XY["Y"] = np.nan, 0.1
    with pytest.raises(Exception) as e_info:
        project_hole(hole, output_epsg="EPSG:4326")
    assert str(e_info.value) == "Coordinates are not finite"
    with pytest.raises(Exception) as e_info:
        flip_xy("Wrong input")

    holes2 = get_object()
    holes_all = holes + holes2.project("Ykj")
    with pytest.raises(Exception) as e_info:
        check_hole_in_country(holes_all, "FI")
    assert "uniform" in str(e_info.value)

    check_hole_in_country(holes2.project("WGS84"), "FI")


def test_holes_projection_errors2():
    holes = get_object()
    hole = holes[2]
    del hole.header.XY["X"]
    del hole.header.XY["Y"]
    with pytest.raises(Exception) as e_info:
        project_hole(hole, output_epsg="EPSG:4326")
    assert str(e_info.value) == "Hole has no coordinates"

    holes = get_object()
    del holes[0].header.XY["X"]
    del holes[0].header.XY["Y"]
    holes2 = project_holes(holes)
    assert len(holes) > len(holes2)

    holes = get_object()
    del holes[1].fileheader.KJ["Coordinate system"]  # del all pointers
    holes2 = project_holes(holes)  # holes2 is empty
    assert len(holes) > len(holes2)

    holes = get_object()
    holes[2].header.XY["X"] = np.nan
    holes[2].header.XY["Y"] = np.nan
    holes2 = project_holes(holes)
    assert len(holes) > len(holes2)


def test_holes_projection_errors3():
    holes = get_object()
    hole = holes[5]
    hole.fileheader.KJ["Coordinate system"] = "UnknownString"
    with pytest.raises(Exception) as e_info:
        project_hole(hole, output_epsg="EPSG:4326")
    assert "Internal Proj Error" in str(e_info.value)


def test_holes_projection_errors4():
    holes = get_object()
    hole = holes[5]
    hole.fileheader.KJ["Coordinate system"] = "UnknownString"
    with pytest.raises(Exception) as e_info:
        check_hole_in_country("These are not holes")
    assert "holes -parameter is unknown input type" == str(e_info.value)
    with pytest.raises(Exception) as e_info:
        project_hole("This is not a hole")
    assert "hole -parameter invalid" == str(e_info.value)
    with pytest.raises(Exception) as e_info:
        check_hole_in_country("This is not a hole")
    assert "input" in str(e_info.value)


def test_lanlot():
    x, y = 6.1, 7.1
    x2, y2 = project_points(x, y, "EPSG:4326")
    assert x == x2
    assert y == y2
    x, y = 6.1, 7.1
    x2, y2 = project_points(x, y, "EPSG:25835")
    assert x != x2
    assert x != x2


@pytest.mark.parametrize(
    "coords",
    [
        [(90872.833, 28754.747), (6690731.332, 24528578.339)],
        [(87869.84, 28400.415), (6687728.356, 24528223.999)],
        [(82933.63, 28916.433), (6682792.148, 24528740.035)],
        [(75574.33, 29421.73), (6675432.852, 24529245.46)],
        [(89426.487, 31047.619), (6689285.055, 24530871.198)],
        [(85044.684, 30305.457), (6684903.24, 24530129.088)],
        [(81230.513, 30215.148), (6681089.051, 24530038.809)],
        [(81012.527, 31976.059), (6680871.105, 24531799.722)],
        [(80006.493, 30110.21), (6679865.025, 24529933.913)],
        [(79566.673, 31602.772), (6679425.244, 24531426.447)],
        [(77358.387, 30417.51), (6677216.935, 24530241.218)],
        [(75133.605, 31334.098), (6674992.184, 24531157.791)],
    ],
)
def test_proj_espoo(coords):
    input_coords, correct = coords
    *output_coords, epsg = proj_espoo(*input_coords)
    assert abs(output_coords[0] - correct[0]) < 0.1
    assert abs(output_coords[1] - correct[1]) < 0.1


@pytest.mark.parametrize(
    "coords",
    [
        [(28837.457, 47640.142), (6683429.958, 25494840.701)],
        [(26072.107, 53177.532), (6680657.986, 25500374.695)],
        [(22175.463, 54384.703), (6676759.94, 25501577.166)],
        [(18508.069, 53483.971), (6673093.675, 25500672.036)],
        [(15202.665, 48527.725), (6669794.273, 25495711.879)],
        [(24445.147, 43691.581), (6679042.451, 25490886.909)],
        [(32735.009, 63831.151), (6687307.994, 25511036.189)],
        [(28450.813, 64725.703), (6683022.777, 25511925.579)],
        [(18273.807, 41850.229), (6672873.404, 25489038.161)],
        [(33467.135, 51878.738), (6688054.481, 25499084.809)],
        [(31322.962, 61293.144), (6685899.016, 25508496.517)],
        [(26342.678, 61934.409), (6680918.025, 25509131.786)],
        [(16210.044, 63851.691), (6670783.215, 25511036.861)],
        [(21762.959, 58838.688), (6676342.086, 25506030.598)],
        [(23049.178, 47564.155), (6677641.844, 25494757.755)],
        [(17250.674, 45299.238), (6671846.137, 25492485.896)],
        [(16605.89, 50411.014), (6671195.215, 25497596.831)],
    ],
)
def test_proj_helsinki(coords):
    input_coords, correct = coords
    *output_coords, epsg = proj_helsinki(*input_coords)
    assert abs(output_coords[0] - correct[0]) < 0.1
    assert abs(output_coords[1] - correct[1]) < 0.1


def test_proj_porvoo():
    input_coords = (0, 0)
    *output_coords, epsg = proj_porvoo(*input_coords)
    assert type(output_coords[0]) == float
    assert type(output_coords[1]) == float
    assert type(epsg) == str


@pytest.mark.parametrize(
    "coords",
    [
        [[7179609.81, 3394211.43], [0.5551]],
        [[7234010.15, 3442347.31], [0.5296]],
        [[6908518.63, 3616919.04], [0.2882]],
        [[7003877.59, 3499226.6], [0.4005]],
        [[6800180.47, 3505475.49], [0.3156]],
        [[7053589.08, 3464391.9], [0.4334]],
        [[6829200.25, 3450289.82], [0.3572]],
        [[6728116.17, 3260951.05], [0.3945]],
        [[6828057.3, 3320271.94], [0.4211]],
        [[7001324.44, 3570398.91], [0.3453]],
        [[7310589.81, 3546761.5], [0.4372]],
        [[7112026.51, 3531025.46], [0.4272]],
        [[6798161.35, 3343554.26], [0.3948]],
        [[6859323.18, 3340179.39], [0.4357]],
        [[7210437.96, 3466288.18], [0.5015]],
    ],
)
def test_height_systems(coords):
    input_coords, correct = coords
    output_height = height_systems_diff(input_coords, "N2000", "N43")
    output_height2 = height_systems_diff(input_coords, "N43", "N2000")
    assert abs(float(output_height) - correct[0]) < 0.01
    assert output_height == -output_height2


def test_height_system_errors():
    with pytest.raises(Exception) as e_info:
        height_systems_diff(np.array([[1, 2, 3]]).T, "N2000", "N43")
    assert "array" in str(e_info.value)
    height_systems_diff(np.array([1, 2]), "N2000", "N2000")


def test_height_holes():
    holes = get_object()
    hole = holes[7]
    hole.fileheader.KJ["Height reference"] = "N43"  # pointer to all holes
    holes2 = project_holes(holes, output_height="N2000")
    hole2 = holes2[5]
    assert hole2.fileheader.KJ["Height reference"] == "N2000"
