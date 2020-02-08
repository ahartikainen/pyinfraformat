"""Utilites to handle coordinates and transformations."""
import logging
import re
from copy import deepcopy
from pyproj import Transformer
from . import core

__all__ = ["project_holes"]

logger = logging.getLogger("pyinfraformat")


def coord_string_fix(input_string):
    """Fix coordinate systems string into machine readable."""
    common_separators = "[,. -:]+"
    if len(input_string) <= 4:
        input_string = "ETRS-" + input_string
    return "-".join(re.split(common_separators, input_string.upper()))


def project_hole(hole, output_epsg="EPSG:4326"):
    """Transform holes -objects coordinates.

    Parameters
    ----------
    hole : hole -object

    Returns
    -------
    hole : hole -object with coordinates transformed
    """
    epsg_systems = {
        "WGS84": "EPSG:4326",
        "ETRS-TM35FIN": "EPSG:3067",
        "ETRS89": "EPSG:4258",
        "ETRS-GK19": "EPSG:3873",
        "ETRS-GK20": "EPSG:3874",
        "ETRS-GK21": "EPSG:3875",
        "ETRS-GK22": "EPSG:3876",
        "ETRS-GK23": "EPSG:3877",
        "ETRS-GK24": "EPSG:3878",
        "ETRS-GK25": "EPSG:3879",
        "ETRS-GK26": "EPSG:3880",
        "ETRS-GK27": "EPSG:3881",
        "ETRS-GK28": "EPSG:3882",
        "ETRS-GK29": "EPSG:3883",
        "ETRS-GK30": "EPSG:3884",
        "ETRS-GK31": "EPSG:3885",
        "ETRS-TM34": "EPSG:3046",
        "ETRS-TM35": "EPSG:3047",
        "ETRS-TM36": "EPSG:3048",
    }
    epsg_names = {epsg_systems[i]: i for i in epsg_systems}
    other_systems = {
        "HESLINKI": "Some_function",
        "ESPOO": "Some_function2",
        "PORVOO": "Some_function3",
    }  # Common finnish systems. Helsinki, espoo...

    if output_epsg not in epsg_names:
        raise ValueError("Unkown or not implemented EPSG as output_epsg")
    if (
        hasattr(hole, "fileheader")
        and hasattr(hole.fileheader, "KJ")
        and "Coordinate system" in hole.fileheader.KJ
        and hasattr(hole, "header")
    ):
        input_str = hole.fileheader.KJ["Coordinate system"]
        input_str = coord_string_fix(input_str)

    else:
        raise ValueError("Hole has no coordinate system")

    if not (hasattr(hole.header, "XY") and "X" in hole.header.XY and "Y" in hole.header.XY):
        raise ValueError("Hole has no coordinates")

    if input_str in epsg_systems:
        input_epsg = epsg_systems[input_str]
    elif input_str in other_systems:
        raise NotImplementedError("{} not yet implemented".format(input_str))
    else:
        msg = "Unkown or not implemented EPSG in holes {}".format(input_str)
        raise ValueError(msg)

    transformer = Transformer.from_crs(input_epsg, output_epsg)
    y, x = hole.header.XY["X"], hole.header.XY["Y"]  # Note x-y change
    x, y = transformer.transform(x, y)
    hole.header.XY["X"], hole.header.XY["Y"] = y, x
    hole.fileheader.KJ["Coordinate system"] = epsg_names[output_epsg]
    return hole


def project_holes(holes, output_epsg="EPSG:4326"):
    """Transform holes -objects coordinates.

    Parameters
    ----------
    holes : holes -object

    Returns
    -------
    holes : holes -object with coordinates transformed
    """
    if isinstance(holes, core.Holes):
        proj_holes = []
        for hole in holes:
            hole = deepcopy(hole)
            proj_holes.append(project_hole(hole, output_epsg=output_epsg))
        return core.Holes(proj_holes)
    elif isinstance(holes, core.Hole):
        hole = deepcopy(holes)
        return project_hole(hole, output_epsg=output_epsg)
    else:
        raise ValueError("holes -parameter is unkown input type")
