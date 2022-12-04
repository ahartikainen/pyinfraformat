"""Utilities to handle coordinates and transformations."""
import logging
from copy import deepcopy
from functools import lru_cache

import numpy as np
import pandas as pd
import pyproj
from matplotlib.tri import LinearTriInterpolator, Triangulation
from pyproj import Transformer

from .core import Hole, Holes

__all__ = ["project_holes"]

logger = logging.getLogger("pyinfraformat")

INTERPOLATORS = {}  # LinearTriInterpolator for height systems. Functions add interpolators.
COUNTRY_BBOX = {
    "FI": ("Finland", [19.0, 59.0, 32.0, 71.0]),
    "EE": ("Estonia", [23.5, 57.0, 29.0, 59.0]),
}


@lru_cache(maxsize=10_000)
def get_transformer(input_system, output_system):
    """Return pyproj transformer, use lru_cache to cache calls."""
    return Transformer.from_crs(input_system, output_system, always_xy=True)


@lru_cache(maxsize=10_000)
def coord_str_recognize(input_string):
    """Try to recognize user input coordinate systems."""
    abbreviations = {
        "HKI": "HELSINKI",
        "YKJ": "KKJ / Finland Uniform Coordinate System",
        "KKJ": "KKJ / Finland Uniform Coordinate System",
        "TM35FIN": "ETRS89 / TM35FIN(E,N)",
    }
    input_string = input_string.upper()
    input_string = abbreviations.get(input_string, input_string)
    if input_string in LOCAL_SYSTEMS:
        return input_string
    try:
        crs = pyproj.CRS.from_user_input(input_string)
    except pyproj.exceptions.CRSError as error:
        error_string = error.args[0]
        if "several objects matching this name" not in error_string:
            raise
        error_string = error_string[error_string.rfind(": ") + 2 : -1]
        projections = error_string.split(",")
        logger.warning(
            ("Several coordinate systems match %s input string %s, assuming %s"),
            projections,
            input_string,
            projections[0],
        )
        crs = pyproj.CRS.from_user_input(projections[0])
    return crs.name


def flip_xy(holes):
    """Change holes x,y to y,x."""
    if isinstance(holes, Holes):
        holes_copy = deepcopy(holes)
        for hole in holes_copy:
            if (
                hasattr(hole, "header")
                and hasattr(hole.header, "XY")
                and "X" in hole.header.XY
                and "Y" in hole.header.XY
            ):
                hole.header.XY["X"], hole.header.XY["Y"] = (
                    hole.header.XY["Y"],
                    hole.header.XY["X"],
                )
        return holes_copy
    if isinstance(holes, Hole):
        hole_copy = deepcopy(holes)
        if (
            hasattr(hole_copy, "header")
            and hasattr(hole_copy.header, "XY")
            and "X" in hole_copy.header.XY
            and "Y" in hole_copy.header.XY
        ):
            hole_copy.header.XY["X"], hole_copy.header.XY["Y"] = (
                hole_copy.header.XY["Y"],
                hole_copy.header.XY["X"],
            )
        return hole_copy
    raise ValueError("Inappropriate argument.")


def proj_espoo(x, y):
    """Project Espoo vvj coordinates into ETRS-GK24 (EPSG:3878).

    https://www.espoo.fi/fi-FI/Asuminen_ja_ymparisto/Rakentaminen/Kiinteiston_muodostus/Koordinaattiuudistus(19923)  # pylint: disable=line-too-long
    """
    # pylint: disable=invalid-name
    output_epsg = "EPSG:3878"
    a = 6599858.007479810200000
    b = 24499824.978235636000000
    c = 0.999998786628487
    d = 0.000020762261526
    e = -0.000014784506306
    f = 0.999996546603269
    x, y = a + c * x + d * y, b + e * x + f * y
    return x, y, output_epsg


def proj_helsinki(x, y):
    """Project Helsinki coordinates into ETRS-GK25 (EPSG:3879).

    https://www.hel.fi/helsinki/fi/kartat-ja-liikenne/kartat-ja-paikkatieto/paikkatiedot+ja+-aineistot/koordinaatistot_ja+_korkeudet/koordinaatti_ja_korkeusjarjestelmat # pylint: disable=line-too-long
    """
    # pylint: disable=invalid-name
    output_epsg = "EPSG:3879"
    a = 6654650.14636
    b = 25447166.49457
    c = 0.99998725362
    d = -0.00120230340
    e = 0.00120230340
    f = 0.99998725362
    x, y = a + c * x + d * y, b + e * x + f * y
    return x, y, output_epsg


def proj_porvoo(x, y):
    """Project Porvoo coordinates into KKJ3 (EPSG:2393).

    https://www.porvoo.fi/koordinaatti-ja-korkeusjarjestelma
    """
    # pylint: disable=invalid-name
    output_epsg = "EPSG:2393"
    P = x - 6699461.017
    I = y - 427129.490
    x = 6699460.034 + 1.0000817225 * P - 0.0000927982 * I
    y = 3427132.007 + 1.0000817225 * I + 0.0000927982 * P

    return x, y, output_epsg


LOCAL_SYSTEMS = {"HELSINKI": proj_helsinki, "ESPOO": proj_espoo, "PORVOO": proj_porvoo}


def project_points(x, y, input_system="EPSG:3067", output_system="EPSG:4326"):
    """Transform coordinate points from input to output, default output WGS84.

    Parameters
    ----------
    x : list or float
    x : list or float
    input_system : str
        ESPG code, 'EPSG:XXXX' or name of the coordinate system.
    output_system : str
        ESPG code, 'EPSG:XXXX' or name of the coordinate system.

    Returns
    -------
    x : list or float
    y : list or float
    """
    input_system = str(input_system).upper()
    if "EPSG" in input_system:
        input_epsg = input_system
    else:
        input_epsg = coord_str_recognize(input_system)
        if "unrecognized format" in input_epsg.lower():
            raise ValueError(
                "Unrecognized format / unknown name for input_system parameter {}".format(
                    input_epsg
                )
            )
    output_system = str(output_system).upper()
    if "EPSG" in output_system:
        output_epsg = output_system
    else:
        output_epsg = coord_str_recognize(output_system)
        if "unrecognized format" in output_epsg.lower():
            raise ValueError(
                "Unrecognized format / unknown name for output_system parameter {}".format(
                    input_epsg
                )
            )

    if input_epsg == output_epsg:
        return x, y
    transf = get_transformer(input_epsg, output_epsg)
    y, x = transf.transform(y, x)  # pylint: disable=unpacking-non-sequence
    return x, y


def check_hole_inside_bbox(hole, bbox):
    """Check if hole point is inside bbox.

    Returns boolean.
    """
    if hasattr(hole.header, "XY") and "X" in hole.header.XY and "Y" in hole.header.XY:
        x, y = hole.header.XY["X"], hole.header.XY["Y"]
        return bbox[1] < x < bbox[3] and bbox[0] < y < bbox[2]
    return False


def check_hole_in_country(holes, country="FI"):
    """Check if holes or hole points are inside country bbox. Has to be in some system with EPSG.

    Returns boolean.
    """
    if isinstance(holes, Holes):
        if len(holes) == 0:
            return True
        input_str = holes[0].fileheader.KJ["Coordinate system"]
        if not all(hole.fileheader.KJ["Coordinate system"] == input_str for hole in holes):
            raise ValueError("Input not in uniform coordinate system")
    elif isinstance(holes, Hole):
        input_str = holes.fileheader.KJ["Coordinate system"]
    else:
        raise ValueError("holes -parameter is unknown input type")
    input_str = coord_str_recognize(input_str)

    bbox = COUNTRY_BBOX[country][1].copy()
    if input_str != "EPSG:4326":
        transf = get_transformer("EPSG:4326", input_str)
        # pylint: disable=unpacking-non-sequence
        bbox[0], bbox[1] = transf.transform(bbox[0], bbox[1])
        # pylint: disable=unpacking-non-sequence
        bbox[2], bbox[3] = transf.transform(bbox[2], bbox[3])

    else:
        raise ValueError("Input has to be in known epsg system.", input_str)
    if isinstance(holes, Holes):
        return all(check_hole_inside_bbox(hole, bbox) for hole in holes)
    else:
        return check_hole_inside_bbox(holes, bbox)


def get_n43_n60_points():
    """Get MML reference points for height systems n43-n60."""
    url = r"https://www.maanmittauslaitos.fi/sites/maanmittauslaitos.fi/files/attachments/2019/02/n43n60triangulationVertices.txt"  # pylint: disable=line-too-long
    df = pd.read_csv(url, delim_whitespace=True, header=None)
    df.columns = ["Point", "X", "Y", "diff", "Karttalehden numero"]
    df.index = df.iloc[:, 0]
    df = df.loc[:, ["X", "Y", "diff"]]
    df["diff"] = df["diff"] * 0.001
    return df


def get_n43_n60_triangulation():
    """Get MML triangles for height systems n43-n60."""
    url = r"https://www.maanmittauslaitos.fi/sites/maanmittauslaitos.fi/files/attachments/2019/02/n43n60triangulationNetwork.txt"  # pylint: disable=line-too-long
    df = pd.read_csv(url, delim_whitespace=True, header=None)
    return df


def get_n43_n60_interpolator():
    """Get interpolator for N43 to N60 height system change, data from MML."""
    df_points = get_n43_n60_points()
    df_tri = get_n43_n60_triangulation()
    triangles = df_tri.replace(
        df_points.index.values, np.arange(df_points.shape[0], dtype=int)
    ).values
    interpolator_ = Triangulation(df_points["X"], df_points["Y"], triangles)
    interpolator = LinearTriInterpolator(interpolator_, df_points["diff"])
    return interpolator


def get_n60_n2000_points():
    """Get MML reference points for height systems n60-n2000."""
    url = r"https://www.maanmittauslaitos.fi/sites/maanmittauslaitos.fi/files/attachments/2019/02/n60n2000triangulationVertices.txt"  # pylint: disable=line-too-long
    df = pd.read_csv(url, encoding="latin-1", delim_whitespace=True, header=None)
    df.columns = ["Point", "X", "Y", "N60", "N2000"]
    df.index = df.iloc[:, 0]
    df["diff"] = df["N2000"] - df["N60"]
    df = df.loc[:, ["X", "Y", "diff"]]
    return df


def get_n60_n2000_triangulation():
    """Get MML triangles for height systems n60-n2000."""
    url = r"https://www.maanmittauslaitos.fi/sites/maanmittauslaitos.fi/files/attachments/2019/02/n60n2000triangulationNetwork.txt"  # pylint: disable=line-too-long
    df = pd.read_csv(url, encoding="latin-1", delim_whitespace=True, header=None)
    return df


def get_n60_n2000_interpolator():
    """Get interpolator for N60 to N2000 height system change, data from MML."""
    df_points = get_n60_n2000_points()
    df_tri = get_n60_n2000_triangulation()
    triangles = df_tri.replace(
        df_points.index.values, np.arange(df_points.shape[0], dtype=int)
    ).values
    interpolator_ = Triangulation(df_points["X"], df_points["Y"], triangles)
    interpolator = LinearTriInterpolator(interpolator_, df_points["diff"])
    return interpolator


def height_systems_diff(points, input_system, output_system):
    """Get difference between systems at certain point.

    Calculates the difference for height systems at points based on MML reference points
    and triangulation. Coordinate system is KKJ3 (EPSG:2393).

    Parameters
    ----------
    points: array_like of shape (n, 2)
        points where to calculate the difference. Points in KKJ3.
    input_system: str
        height system as input. Possible values: N43, N60, N2000
    output_system: str
        height system as output. Possible values: N43, N60, N2000

    Returns
    -------
    ndarray
        list of height differences (mm). Nan for points outside triangulation.
    """
    points = np.asarray(points)
    if len(points.shape) == 1 and len(points) == 2:
        points = points[None, :]
    if points.shape[1] != 2:
        raise ValueError("Points has to be 2D -array with shape=(n, 2)")
    input_system = input_system.upper()
    output_system = output_system.upper()
    if input_system == output_system:
        return 0.0
    if input_system == "N43" and output_system == "N2000":
        diff = height_systems_diff(points, "N43", "N60")
        diff += height_systems_diff(points, "N60", "N2000")
        return diff
    elif output_system == "N43" and input_system == "N2000":
        diff = -height_systems_diff(points, "N43", "N60")
        diff -= height_systems_diff(points, "N60", "N2000")
        return diff

    if input_system == "N43" and output_system == "N60":
        key = (input_system, output_system)
        if key not in INTERPOLATORS:
            INTERPOLATORS[key] = get_n43_n60_interpolator()
        diff = INTERPOLATORS[key](*points.T).data
    elif input_system == "N60" and output_system == "N43":
        key = (output_system, input_system)
        if key not in INTERPOLATORS:
            INTERPOLATORS[key] = get_n43_n60_interpolator()
        diff = -INTERPOLATORS[key](*points.T).data
    elif input_system == "N60" and output_system == "N2000":
        key = (input_system, output_system)
        if key not in INTERPOLATORS:
            INTERPOLATORS[key] = get_n60_n2000_interpolator()
        diff = INTERPOLATORS[key](*points.T).data
    elif input_system == "N2000" and output_system == "N60":
        key = (output_system, input_system)
        if key not in INTERPOLATORS:
            INTERPOLATORS[key] = get_n60_n2000_interpolator()
        diff = -INTERPOLATORS[key](*points.T).data
    else:
        raise ValueError(
            (
                "input_system ({}) or output_system ({}) invalid."
                " Possible values are N43, N60, N2000."
            ).format(input_system, output_system)
        )
    return -diff


def project_hole(hole, output_epsg="EPSG:4326", output_height=False):
    """Transform hole -objects coordinates.

    Parameters
    ----------
    hole : hole -object
    output_epsg : str
        ESPG code, EPSG:XXXX
    output_height : str
        output height system. Possible values N43, N60, N2000 and False.
        False for no height system change or checks.

    Returns
    -------
    hole : Hole -object
        Copy of hole with coordinates transformed
    """
    hole_copy = deepcopy(hole)
    if not isinstance(hole, Hole):
        raise ValueError("hole -parameter invalid")

    output_epsg = coord_str_recognize(output_epsg)
    if "unrecognized format" in output_epsg.lower():
        raise ValueError("Unrecognized format / unknown name as output_epsg")
    if (
        hasattr(hole_copy, "fileheader")
        and hasattr(hole_copy.fileheader, "KJ")
        and "Coordinate system" in hole_copy.fileheader.KJ
        and hasattr(hole_copy, "header")
    ):
        input_str = hole_copy.fileheader.KJ["Coordinate system"]
        input_str = coord_str_recognize(input_str)

    else:
        raise ValueError("Hole has no coordinate system")

    if (
        hasattr(hole_copy.header, "XY")
        and "X" in hole_copy.header.XY
        and "Y" in hole_copy.header.XY
    ):
        x, y = hole_copy.header.XY["X"], hole_copy.header.XY["Y"]
        if not np.isfinite(x) or not np.isfinite(y):
            raise ValueError("Coordinates are not finite")
    else:
        raise ValueError("Hole has no coordinates")

    if input_str in LOCAL_SYSTEMS:
        func = LOCAL_SYSTEMS[input_str]
        x, y, input_str = func(x, y)
    elif "unrecognized format" in input_str.lower():
        raise ValueError("Unrecognized format / unknown name EPSG in holes {}".format(input_str))

    transf = get_transformer(input_str, output_epsg)
    y, x = transf.transform(y, x)  # pylint: disable=unpacking-non-sequence
    hole_copy.header.XY["X"], hole_copy.header.XY["Y"] = x, y

    hole_copy.fileheader.KJ["Coordinate system"] = output_epsg

    if not output_height:
        return hole_copy

    transf = get_transformer(output_epsg, "EPSG:2393")
    point = transf.transform(y, x)

    try:
        input_system = hole.fileheader["KJ"]["Height reference"]
    except KeyError as error:
        raise ValueError("Hole has no height system") from error

    if input_system not in ["N43", "N60", "N2000"]:
        raise ValueError("Hole has unknown heigth system:", input_system)

    diff = height_systems_diff(point, input_system, output_height)
    hole_copy.header.XY["Z-start"] += round(float(diff), 3)
    hole_copy.fileheader["KJ"]["Height reference"] = output_height
    return hole_copy


def project_holes(holes, output="EPSG:4326", check="Finland", output_height=False):
    """Transform holes -objects coordinates.

    Transform holes coordinates, drops invalid holes.

    Parameters
    ----------
    holes : holes or hole -object
    output : str
        ESPG code, 'EPSG:XXXX' or name of the coordinate system.
    check : str
        Check if points are inside area. Raises warning into logger.
        Possible values: 'Finland', 'Estonia', False
    output_height : str
        output height system. Possible values N43, N60, N2000 and False.
        False for no height system change or checks.

    Returns
    -------
    holes : Holes -object
        Copy of holes with coordinates transformed

    Examples
    --------
    holes_gk25 = project_holes(holes, output_epsg="EPSG:3879", check="Finland")
    one_hole_gk24 = project_holes(one_hole, output_epsg="EPSG:3878", check="Estonia")
    """
    output = str(output).upper()
    output_epsg = coord_str_recognize(output)
    if "unknown" in output_epsg.lower():
        raise ValueError(
            "Unrecognized format / unknown name for output parameter {}".format(output)
        )
    if isinstance(holes, Holes):
        proj_holes = []
        for hole in holes:
            try:
                hole_copy = project_hole(hole, output_epsg, output_height)
            except ValueError as error:
                error_str = str(error)
                if error_str == "Hole has no coordinate system":
                    logger.warning(error_str)
                    continue
                if str(error) == "Coordinates are not finite":
                    logger.warning(error_str)
                    continue
                if str(error) == "Hole has no coordinates":
                    logger.warning(error_str)
                    continue
                raise ValueError(error) from error
            proj_holes.append(hole_copy)
        return_value = Holes(proj_holes)
    elif isinstance(holes, Hole):
        hole = deepcopy(holes)
        return_value = project_hole(hole, output_epsg, output_height)
    else:
        raise ValueError("holes -parameter is unknown input type")

    if check and check.upper() == "FINLAND":
        if not check_hole_in_country(return_value, "FI"):
            msg = "Holes are not inside Finland"
            logger.critical(msg)
    if check and check.upper() == "ESTONIA":
        if not check_hole_in_country(return_value, "EE"):
            msg = "Holes are not inside Estonia"
            logger.critical(msg)
    return return_value
