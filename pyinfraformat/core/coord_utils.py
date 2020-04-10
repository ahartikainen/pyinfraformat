"""Utilites to handle coordinates and transformations."""
import logging
import re
from copy import deepcopy
from pyproj import Transformer
from .core import Holes, Hole

__all__ = ["project_holes"]

logger = logging.getLogger("pyinfraformat")

TRANSFORMERS = {}  # dict of pyproj Transformers, key (input, output)


def coord_string_fix(input_string):
    """Try to fix coordinate systems string into machine readable."""
    common_separators = r"[,. :\-]"
    if len(input_string) <= 4:
        input_string = "ETRS-" + input_string
    return "-".join(re.split(common_separators, input_string.upper()))


def proj_espoo(x, y):
    """Project Espoo vvj coordinates into ETRS-GK25 (EPSG:3879).

    https://www.espoo.fi/fi-FI/Asuminen_ja_ymparisto/Rakentaminen
    /Kiinteiston_muodostus/Koordinaattiuudistus(19923)
    """
    # pylint: disable=invalid-name
    output_epsg = "EPSG:3879"
    a = 6600290.731951121200000
    b = 25443205.726901203000000
    c = 0.999869662254702
    d = -0.015128383929030
    e = 0.015134113397130
    f = 0.999867560105837
    x, y = a + c * x + d * y, b + e * x + f * y
    return x, y, output_epsg


def proj_helsinki(x, y):
    """Project Helsinki coordinates into ETRS-GK25 (EPSG:3879).

    https://www.hel.fi/helsinki/fi/kartat-ja-liikenne/kartat-ja-paikkatieto
    /paikkatiedot+ja+-aineistot/koordinaatistot_ja+_korkeudet/koordinaatti_ja_korkeusjarjestelmat
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


def get_epsg_systems():
    """Get dict of epsg systems, {name: epsg code}."""
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
    return epsg_systems


def to_lanlot(x, y, input_epsg="EPSG:3067"):
    """Transform coordinates to WGS84.

    Parameters
    ----------
    x : list or float
    x : list or float
    intput_epsg : str

    Returns
    -------
    x : list or float
    y : list or float
    """
    output_epsg = "EPSG:4326"
    if input_epsg == output_epsg:
        return x, y
    key = (input_epsg, output_epsg)
    if key in TRANSFORMERS:
        transf = TRANSFORMERS[key]
    else:
        transf = Transformer.from_crs(input_epsg, output_epsg)
        TRANSFORMERS[key] = transf
    x, y = transf.transform(x, y)
    return x, y


def project_hole(hole, output_epsg="EPSG:4326"):
    """Transform holes -objects coordinates.

    Parameters
    ----------
    hole : hole -object
    output_epsg : str
        ESPG code, EPSG:XXXX

    Returns
    -------
    hole : hole -object with coordinates transformed
    """
    epsg_systems = get_epsg_systems()
    epsg_names = {epsg_systems[i]: i for i in epsg_systems}
    other_systems = {
        "HELSINKI": proj_helsinki,
        "ESPOO": proj_espoo,
        "PORVOO": proj_porvoo,
    }  # Common finnish systems. Helsinki, espoo...

    hole_copy = deepcopy(hole)
    if output_epsg not in epsg_names:
        raise ValueError("Unkown or not implemented EPSG as output_epsg")
    if (
        hasattr(hole_copy, "fileheader")
        and hasattr(hole_copy.fileheader, "KJ")
        and "Coordinate system" in hole_copy.fileheader.KJ
        and hasattr(hole_copy, "header")
    ):
        input_str = hole_copy.fileheader.KJ["Coordinate system"]
        input_str = coord_string_fix(input_str)

    else:
        raise ValueError("Hole has no coordinate system")

    if (
        hasattr(hole_copy.header, "XY")
        and "X" in hole_copy.header.XY
        and "Y" in hole_copy.header.XY
    ):
        y, x = hole_copy.header.XY["X"], hole_copy.header.XY["Y"]  # Note x-y change
    else:
        raise ValueError("Hole has no coordinates")

    if input_str in epsg_systems:
        input_epsg = epsg_systems[input_str]
    elif input_str in other_systems:
        func = other_systems[input_str]
        x, y, input_epsg = func(x, y)
    else:
        msg = "Unkown or not implemented EPSG in holes {}".format(input_str)
        raise ValueError(msg)

    key = (input_epsg, output_epsg)
    if key in TRANSFORMERS:
        transf = TRANSFORMERS[key]
    else:
        transf = Transformer.from_crs(input_epsg, output_epsg)
        TRANSFORMERS[key] = transf
    x, y = transf.transform(x, y)
    hole_copy.header.XY["X"], hole_copy.header.XY["Y"] = y, x
    hole_copy.fileheader.KJ["Coordinate system"] = epsg_names[output_epsg]
    return hole_copy


def project_holes(holes, output_epsg="EPSG:4326"):
    """Transform holes -objects coordinates.

    Parameters
    ----------
    holes : holes -object
    output_epsg : str
        ESPG code, EPSG:XXXX

    Returns
    -------
    holes : holes -object with coordinates transformed
    """
    if isinstance(holes, Holes) or len(holes) > 1:
        proj_holes = []
        for hole in holes:
            try:
                hole_copy = project_hole(hole, output_epsg=output_epsg)
            except ValueError as e:
                if str(e)=="Hole has no coordinate system":
                    continue
                else:
                    raise ValueError(e)
            proj_holes.append(hole_copy)
        return Holes(proj_holes)
    elif isinstance(holes, Hole):
        hole = deepcopy(holes)
        return project_hole(hole, output_epsg=output_epsg)
    else:
        raise ValueError("holes -parameter is unkown input type")
