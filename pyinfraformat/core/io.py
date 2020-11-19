# pylint: disable=try-except-raise
"""Input and output methods."""
import json
import logging
import os
from collections import Counter
from glob import glob

from owslib.wfs import WebFeatureService

from ..exceptions import PathNotFoundError
from .coord_utils import project_points
from .core import Hole, Holes
from .utils import identifiers, is_number

logger = logging.getLogger("pyinfraformat")
logger.propagate = False

__all__ = ["from_infraformat", "from_gtk_wfs"]

# pylint: disable=redefined-argument-from-local
def from_infraformat(path=None, encoding="utf-8", extension=None, robust=True):
    """Read inframodel file(s).

    Paramaters
    ----------
    path : str, optional, default None
        path to read data (file / folder / glob statement)
    encoding : str or list of str, optional, default 'utf-8'
        file encoding, if 'utf-8' fails, code will try to use 'latin-1'.
        If input is a list, will try to read with path in given order.
    use_glob : bool, optional, default False
        path is a glob string
    extension : bool, optional, default None
    robust : bool, optional, default False
        If True, enable reading files with ill-defined/illegal lines.

    Returns
    -------
    Holes -object
    """
    if path is None or not path:
        return Holes()
    if os.path.isdir(path):
        if extension is None:
            filelist = glob(os.path.join(path, "*"))
        else:
            if not extension.startswith("."):
                extension = ".{}".format(extension)
            filelist = glob(os.path.join(path, "*{}".format(extension)))
    else:
        filelist = glob(path)
        if not filelist:
            raise PathNotFoundError("{}".format(path))

    if isinstance(encoding, str):
        encoding_list = [encoding]

    hole_list = []
    if robust:
        # Common encoding types
        common_encoding = [
            "utf-8",
            "latin-1",
            "cp1252",
            "iso8859_10",
            "ascii",
            "utf-16",
        ]
        n_user_encoding = len(encoding_list)
        encoding, *common_encoding = list(encoding_list) + common_encoding

        for filepath in filelist:
            try:
                holes = read(filepath, encoding=encoding, robust=robust)
            except (UnicodeDecodeError, UnicodeEncodeError, UnicodeError):
                holes = None
                for i, encoding in enumerate(common_encoding, 1):
                    try:
                        holes = read(filepath, encoding=encoding, robust=robust)
                    except (UnicodeDecodeError, UnicodeEncodeError, UnicodeError):
                        continue
                    except:
                        raise
                    else:
                        if i > n_user_encoding:
                            msg = "Non-default encoding used for reading: {}".format(encoding)
                            logger.info(msg)
            except:
                raise
            if holes:
                hole_list.extend(holes)
    else:
        fileread_failed = False
        for filepath in filelist:
            for encoding in encoding_list:
                try:
                    holes = read(filepath, encoding=encoding, robust=robust)
                    fileread_failed = False
                except (UnicodeDecodeError, UnicodeEncodeError, UnicodeError):
                    fileread_failed = True
                    continue
                except:
                    raise
                hole_list.extend(holes)
        if fileread_failed:
            raise  # pylint: disable=misplaced-bare-raise

    return Holes(hole_list)


def from_gtk_wfs(bbox, coord_system, robust=True, maxholes=1000):
    """Get holes from GTK WFS.

    Paramaters
    ----------
    bbox : tuple
        bbox to get data from.
        Is form (x1, y1, x2, y2).
    coord_system : str
        ESPG code of bbox, 'EPSG:XXXX' or name of the coordinate system.
        Check pyinfraformat.coord_utils.EPSG_SYSTEMS for possible values.
    robust : bool, optional, default False
        If True, enable reading files with ill-defined/illegal lines.
    maxholes : int, optional, default 1000
        Maximum number of points to get from wfs.


    Returns
    -------
    Holes -object

    Examples
    --------
    bbox = (60, 24, 61, 25)
    holes = from_gtk_wfs(bbox, coord_system="EPSG:4326", robust=True)
    """
    # pylint: disable=invalid-name
    url = "http://gtkdata.gtk.fi/arcgis/services/Rajapinnat/GTK_Pohjatutkimukset_WFS/MapServer/WFSServer?"  # pylint: disable=line-too-long
    wfs = WebFeatureService(url, version="2.0.0")

    x1, y1 = project_points(bbox[0], bbox[1], coord_system, "EPSG:4326")
    x2, y2 = project_points(bbox[2], bbox[3], coord_system, "EPSG:4326")

    x1, x2 = min((x1, x2)), max((x1, x2))
    y1, y2 = min((y1, y2)), max((y1, y2))
    bbox = [x1, y1, x2, y2]

    wfs_io = wfs.getfeature(
        typename=["Rajapinnat_GTK_Pohjatutkimukset_WFS:Pohjatutkimukset"],
        maxfeatures=maxholes,
        bbox=bbox,
        outputFormat="GEOJSON",
    )

    data = wfs_io.read().decode("utf-8")
    data = data.replace("\\", r"\\")
    data_json = json.loads(data, strict=False)
    if "features" not in data_json:
        return Holes()

    results = []
    for line in data_json["features"]:
        results.append(line)
    holes = []

    def parse_line(line):
        if ("properties" in line) and ("ALKUPERAINEN_DATA" in line["properties"]):
            hole_str = line["properties"]["ALKUPERAINEN_DATA"].splitlines()
            hole = parse_hole(enumerate(hole_str), robust=robust)
        else:
            hole = Hole()
        hole.add_header("OM", {"Owner": line.get("properties", dict()).get("OMISTAJA", "-")})

        x, y = line["geometry"]["coordinates"]
        x, y = round(float(y), 4), round(float(x), 4)
        if not hasattr(hole.header, "XY"):
            file_xy = {"X": None, "Y": None}
            hole.add_header("XY", file_xy)
        hole.header.XY["X"], hole.header.XY["Y"] = x, y  # pylint: disable=E1101
        file_fo = {"Format version": "?", "Software": "GTK_WFS"}
        hole.add_fileheader("FO", file_fo)
        file_kj = {
            "Coordinate system": "ETRS-TM35FIN",
            "Height reference": line["properties"]["KORKEUSJARJ"],
        }
        hole.add_fileheader("KJ", file_kj)
        return hole

    for i, line in enumerate(results):
        hole = None
        try:
            hole = parse_line(line)
        except KeyError as error:
            msg = "Wfs hole parse failed, line {}. Missing {}".format(i, error)
            logger.warning(msg)
        if hole:
            holes.append(hole)

    holes = Holes(holes)
    return holes


def to_infraformat(data, path, comments=True, fo=None, kj=None, write_mode="w"):
    """Export data to infraformat.

    Parameters
    ----------
    data : list
        A list containing hole data.
    path : str
        Path to save data.
    fo : dict
        Dictionary for fileformat.
        Contains:
            - 'Format version', default 2.3
            - 'Software', default 'pyinfraformat'
            - 'Software version', default 'str(__version__)'
    kj : dict
        Dictionary  for coordinate system.
        Contains:
            - 'Coordinate system', defaults to mode(data)
            - 'Height reference', defaults to mode(data)
        Defaults to mode of the holes.
    write_mode : str
        By default create a new file.
        If "wa" appends to current file and it is recommended to set fo and kj to False.
    """
    with open(path, mode=write_mode) as f:
        write_fileheader(data, f, fo=fo, kj=kj)
        for hole in data:
            write_header(hole.header, f)
            write_body(hole, f, comments=comments)


def write_fileheader(data, f, fo=None, kj=None):
    """Write fileheader format out.

    Parameters
    ----------
    data : Infraformat
    f : fileobject
    fo : dict, optional
        Dictionary for fileformat, software and software version.
    kj : dict, optional
        Dictionary for Coordinate system and Height reference.
    """
    if fo is None:
        from ..__init__ import __version__

        fo = {
            "Format version": "2.5",
            "Software": "pyinfraformat",
            "Software version": str(__version__),
        }
    if kj is None:
        try:
            # add coord transformations
            coord = []
            height = []
            for hole in data:
                if hasattr(hole.fileheader, "KJ"):
                    coord.append(hole.fileheader.KJ["Coordinate system"])
                    height.append(hole.fileheader.KJ["Height reference"])
            ((coord, _),) = Counter(coord).most_common(1)
            ((height, _),) = Counter(height).most_common(1)
            kj = {"Coordinate system": coord, "Height reference": height}
        except:
            kj = {"Coordinate system": "-", "Height reference": "-"}

    for key, subdict in {"FO": fo, "KJ": kj}.items():
        line_string = [key]
        for _, value in subdict.items():
            if value is False:
                continue
            line_string.append(str(value))
        if len(line_string) > 1:
            print(" ".join(line_string), file=f)


def write_header(header, f):
    """Write header format out.

    Parameters
    ----------
    header : Header object
    f : fileobject
    """
    header_keys = list(identifiers()[1].keys())
    for key in header_keys:
        if key == "-1":
            continue
        header_string = []
        if hasattr(header, key):
            header_string.append(key)
            attr = getattr(header, key)
            for key_, value in attr.items():
                if key_ == "linenumber":
                    continue
                header_string.append(str(value))
            print(" ".join(header_string), file=f)


# pylint: disable=protected-access
def write_body(hole, f, comments=True, illegal=False, body_spacer=None, body_spacer_start=None):
    """Write data out.

    Parameters
    ----------
    hole : Hole object
    f : fileobject
    comments : bool
    illegal : bool
    body_spacer : str
        str used as a spacer in the body part. Defaults to 4 spaces.
    body_spacer_start : str
        str used as a spacer in the start of the body part. Defaults to 4 spaces.
    """
    if body_spacer is None:
        body_spacer = " " * 4
    if body_spacer_start is None:
        body_spacer_start = " " * 4
    body_text = {}
    # Gather survey information
    line_dict = {}
    for line_dict in hole.survey.data:
        line_string = body_spacer_start + "{}".format(body_spacer).join(
            [str(value) for key, value in line_dict.items() if key != "linenumber"]
        )
        if int(line_dict["linenumber"]) not in body_text:
            body_text[line_dict["linenumber"]] = line_string
        else:
            # duplicate linenumbers
            linenumber = float(line_dict["linenumber"])
            increment = 0.5
            linenumber += increment
            while linenumber in body_text:
                increment /= 2
                linenumber += increment
            body_text[int(linenumber)] = line_string

    # Gather inline comments
    if comments:
        for comment_head, comment_dict in hole.inline_comment.data:
            line_string = (
                "  "
                + str(comment_head)
                + " "
                + " ".join(
                    [str(value) for key, value in comment_dict.items() if key != "linenumber"]
                )
            )
            if int(comment_dict["linenumber"]) not in body_text:
                body_text[int(comment_dict["linenumber"])] = line_string
            else:
                # duplicate linenumbers
                linenumber = float(line_dict["linenumber"])
                increment = 0.5
                linenumber += increment
                while linenumber in body_text:
                    increment /= 2
                    linenumber += increment
                body_text[float(linenumber)] = line_string

    # Gather illegal lines
    if illegal:
        for linenumber, line_string in hole._illegal.data:
            if int(linenumber) not in body_text:
                body_text[int(line_dict["linenumber"])] = line_string
            else:
                # duplicate linenumbers
                linenumber = float(linenumber)
                increment = 0.5
                linenumber += increment
                while linenumber in body_text:
                    increment /= 2
                    linenumber += increment
                body_text[float(linenumber)] = line_string

    if hasattr(hole.header, "-1"):
        ending = getattr(hole.header, "-1")
        linenumber = max(body_text.keys()) + 1
        body_text[float(linenumber)] = "-1 " + " ".join(map(str, ending.values()))

    # print to file
    for key in sorted(body_text.keys()):
        print(body_text[key], file=f)


def read(path, encoding="utf-8", robust=False):
    """Read input data.

    Paramaters
    ----------
    path : str, optional, default None
        path to read data (file / folder / glob statement, see use_glob)
    encoding : str, optional, default 'utf-8'
    robust : bool, optional, default False
        If True, enable reading files with ill-defined/illegal lines.
    """
    file_header_identifiers, *_ = identifiers()

    fileheaders = {}
    holes = []
    with open(path, "r", encoding=encoding) as f:
        holestr_list = []
        for linenumber, line in enumerate(f):
            if not line.strip():
                continue
            head, *tail = line.split(maxsplit=1)
            # Check if head is fileheader
            if head.upper() in file_header_identifiers:
                tail = tail[0].strip().split() if tail else []
                names, dtypes, _ = file_header_identifiers[head.upper()]
                fileheader = {key: format(value) for key, format, value in zip(names, dtypes, tail)}
                fileheaders[head.upper()] = fileheader
            # make this robust check with peek
            elif head == "-1":
                hole_object = parse_hole(holestr_list, robust=robust)
                # Add fileheaders to hole objects
                if fileheaders:
                    for key, value in fileheaders.items():
                        hole_object.add_fileheader(key, value)
                if tail:
                    hole_object.add_header("-1", {"Ending": tail[0].strip()})
                holes.append(hole_object)
                holestr_list = []
            else:
                holestr_list.append((linenumber, line.strip()))
        # check incase that '-1' is not the last line
        if holestr_list:
            hole_object = parse_hole(holestr_list, robust=robust)
            if fileheaders:
                for key, value in fileheaders.items():
                    hole_object.add_fileheader(key, value)
            holes.append(hole_object)
            holestr_list = []

    return holes


def parse_hole(str_list, robust=False):
    """Parse inframodel lines to hole objects.

    Paramaters
    ----------
    str_list : list
        lines as list of strings
    robust : bool, optional, default False
        If True, enable reading files with ill-defined/illegal lines.

    """
    _, header_identifiers, inline_identifiers, survey_identifiers = identifiers()

    hole = Hole()
    survey_type = None
    for linenum, line in str_list:
        if not line.strip():
            continue
        head, *tail = line.split(maxsplit=1)
        head = head.upper()

        if survey_type is None and hasattr(hole.header, "TT"):
            survey_type = getattr(hole.header, "TT").get("Survey abbreviation", None)
            if survey_type:
                survey_type = survey_type.upper()

        illegal_line = False
        try:
            if head in header_identifiers:
                names, dtypes, _ = header_identifiers[head]
                if len(dtypes) == 1:
                    tail = [tail[0].strip()] if tail else []
                else:
                    tail = tail[0].strip().split() if tail else []
                header = {key: format(value) for key, format, value in zip(names, dtypes, tail)}
                header["linenumber"] = linenum
                hole.add_header(head, header)
            elif head in inline_identifiers:
                names, dtypes, _ = inline_identifiers[head]
                if len(dtypes) == 1:
                    tail = [tail[0].strip()] if tail else []
                else:
                    tail = tail[0].strip().split() if tail else []
                inline_comment = {
                    key: format(value) for key, format, value in zip(names, dtypes, tail)
                }
                inline_comment["linenumber"] = linenum
                hole.add_inline_comment(head, inline_comment)
            elif (is_number(head) and survey_type) or survey_type in ("LB",):
                if survey_type != "HP":
                    names, dtypes, _ = survey_identifiers[survey_type]
                    line = line.split(maxsplit=len(dtypes))
                # HP survey is a special case
                else:
                    survey_dict = survey_identifiers[survey_type]
                    if any(item.upper() == "H" for item in line.split()):
                        names, dtypes, _ = survey_dict["H"]
                    else:
                        names, dtypes, _ = survey_dict["P"]

                    line = line.split(maxsplit=len(dtypes))
                survey = {key: format(value) for key, format, value in zip(names, dtypes, line)}
                survey["linenumber"] = linenum
                hole.add_survey(survey)
            else:
                illegal_line = True
                msg = 'Illegal line found! Line {}: "{}"'.format(
                    linenum, line if len(line) < 100 else line[:100] + "..."
                )
                if robust:
                    logger.warning(msg)
                else:
                    logger.critical(msg)
                    raise ValueError(msg)
                hole._add_illegal((linenum, line))  # pylint: disable=protected-access
        except (ValueError, KeyError) as error:
            if not illegal_line:
                msg = 'Illegal line found! Line {}: "{}"'.format(
                    linenum, line if len(line) < 100 else line[:100] + "..."
                )
                if robust:
                    logger.warning(msg)
                else:
                    logger.critical(msg)
                    raise ValueError(msg) from error
            elif not robust:
                raise
            hole._add_illegal((linenum, line))  # pylint: disable=protected-access
    return hole
