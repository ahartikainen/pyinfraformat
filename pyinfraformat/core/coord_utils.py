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


def proj_espoo(x, y):
    """Project Espoo coordinates into ETRS-GK24.

    https://www.espoo.fi/fi-FI/Asuminen_ja_ymparisto/Rakentaminen
    /Kiinteiston_muodostus/Koordinaattiuudistus(19923)
    """
    # pylint: disable=invalid-name
    a = 6599858.007479810200000
    b = 24499824.978235636000000
    c = 0.999998786628487
    d = 0.000020762261526
    e = -0.000014784506306
    f = 0.999996546603269
    return a + c * x + d * y, b + e * x + f * y


def proj_helsinki(x, y):
    """Project Helsinki coordinates into ETRS-GK25.

    https://www.hel.fi/helsinki/fi/kartat-ja-liikenne/kartat-ja-paikkatieto
    /paikkatiedot+ja+-aineistot/koordinaatistot_ja+_korkeudet/koordinaatti_ja_korkeusjarjestelmat
    """
    # pylint: disable=invalid-name
    a = 6654650.14636
    b = 25447166.49457
    c = 0.99998725362
    d = -0.00120230340
    e = 0.00120230340
    f = 0.99998725362
    return a + c * x + d * y, b + e * x + f * y


def proj_porvoo(x, y):
    """Project Helsinki coordinates into KKJ3.

    https://www.porvoo.fi/koordinaatti-ja-korkeusjarjestelma
    """
    # pylint: disable=invalid-name
    P = x - 6699461.017
    I = y - 427129.490
    x = 6699460.034 + 1.0000817225 * P - 0.0000927982 * I
    y = 3427132.007 + 1.0000817225 * I + 0.0000927982 * P
    return x, y


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
