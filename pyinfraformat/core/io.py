# pylint: disable=try-except-raise
"""Input and output methods."""
import io
import json
import logging
import os
import re
from collections import Counter
from contextlib import contextmanager
from glob import glob
from pathlib import Path

import chardet
import requests
from owslib.wfs import WebFeatureService
from tqdm.auto import tqdm

from ..exceptions import PathNotFoundError
from .coord_utils import project_points
from .core import Hole, Holes
from .utils import identifiers, is_nan, is_number

logger = logging.getLogger("pyinfraformat")
logger.propagate = False

__all__ = ["from_infraformat", "from_gtk_wfs"]

TIMEOUT = 36_000

# pylint: disable=redefined-argument-from-local
def from_infraformat(
    path=None, encoding="auto", extension=None, errors="ignore_lines", save_ignored=False
):
    """Read inframodel file(s).

    Paramaters
    ----------
    path : str, optional, default None
        path to read data (file / folder / glob statement)
    encoding : str or list of str, optional, default 'auto'
        file encoding, by default use `chardet` library to find the correct encoding.
    use_glob : bool, optional, default False
        path is a glob string
    extension : bool, optional, default None
    errors : 'ignore_lines', 'ignore_holes', 'force' or 'raise', default 'ignore_lines'
        How to handle ill-defined/illegal lines or holes.
        'force' forces ill-defined values as str and adds error,
        'ignore_lines' passes line as a whole if there is ill-defined values.
    save_ignored : str, StringIO or False, default False
        Append ignored holes or lines to a file. File path str or
        a file-like object (stream) into built-in print function 'file' parameter.

    Returns
    -------
    Holes -object
    """
    if path is None or not path:
        return Holes()

    if isinstance(path, Path):
        path = str(path)

    if isinstance(path, str):
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
    else:
        filelist = [path]

    hole_list = []
    for filepath in filelist:
        holes = read(filepath, encoding=encoding, errors=errors, save_ignored=save_ignored)
        hole_list.extend(holes)

    return Holes(hole_list)


def from_gtk_wfs(
    bbox, coord_system, errors="ignore_lines", save_ignored=False, maxholes=1000, progress_bar=False
):
    """Get holes from GTK WFS.

    Paramaters
    ----------
    bbox : tuple
        bbox to get data from.
        Is form (x1, y1, x2, y2).
    coord_system : str
        ESPG code of bbox, 'EPSG:XXXX' or name of the coordinate system.
    errors : 'ignore_lines', 'ignore_holes', 'force' or 'raise', default 'ignore_lines'
        How to handle ill-defined/illegal lines or holes.
        'force' forces ill-defined values as str and adds error,
        'ignore_lines' passes line as a whole if there is ill-defined values.
    save_ignored : str, StringIO or False, default False
        Append ignored holes or lines to a file. File path str or
        a file-like object (stream) into built-in print function 'file' parameter.
    maxholes : int, optional, default 1000
        Maximum number of points to get from wfs.
    progress_bar : bool

    Returns
    -------
    Holes -object

    Examples
    --------
    bbox = (60, 24, 61, 25)
    holes = from_gtk_wfs(bbox, coord_system="EPSG:4326")
    """
    # pylint: disable=invalid-name
    if errors not in {"ignore_lines", "ignore_holes", "raise", "force"}:
        msg = "Argument errors must be 'ignore_lines', 'ignore_holes', 'raise' or 'force'."
        raise ValueError(msg)
    collected_illegals = []

    url = "http://gtkdata.gtk.fi/arcgis/services/Rajapinnat/GTK_Pohjatutkimukset_WFS/MapServer/WFSServer?"  # pylint: disable=line-too-long
    wfs = WebFeatureService(url, version="2.0.0")

    x1, y1 = project_points(bbox[0], bbox[1], coord_system, "EPSG:4326")
    x2, y2 = project_points(bbox[2], bbox[3], coord_system, "EPSG:4326")
    x1, x2 = min((x1, x2)), max((x1, x2))
    y1, y2 = min((y1, y2)), max((y1, y2))
    bbox = [x1, y1, x2, y2]

    holes = Holes()
    page_size = 1000
    if progress_bar:
        params = {
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetFeature",
            "bbox": "{},{},{},{}".format(*bbox),
            "crs": "EPSG::3067",
            "typenames": "Rajapinnat_GTK_Pohjatutkimukset_WFS:Pohjatutkimukset",
            "resultType": "hits",
        }
        r = requests.get(url, params=params, timeout=TIMEOUT)
        for item in r.text.split():
            if "numberMatched" in item:
                holes_found = int(item.split("=")[1].replace('"', ""))
        pbar = tqdm(total=min([holes_found, maxholes]))

    def parse_line(line):

        if ("properties" in line) and ("ALKUPERAINEN_DATA" in line["properties"]):
            hole_str = line["properties"]["ALKUPERAINEN_DATA"].replace("\\r", "\n").splitlines()
            if errors == "ignore_holes":
                hole, illegal_rows = parse_hole(enumerate(hole_str), force=False)
                if illegal_rows:
                    if save_ignored:
                        collected_illegals.extend(hole_str)
                    return False
            elif errors in {"ignore_lines", "raise"}:
                hole, illegal_rows = parse_hole(enumerate(hole_str), force=False)
                if illegal_rows and save_ignored:
                    collected_illegals.extend(illegal_rows)
            elif errors == "force":
                hole, illegal_rows = parse_hole(enumerate(hole_str), force=True)
                if illegal_rows and save_ignored:
                    collected_illegals.extend(illegal_rows)

            if illegal_rows:
                hole_id = hole.get("header_XY_Point ID", "-")
                index = len(holes) if hole else "-"
                msg = f"Hole {index} / Point ID: {hole_id} has {len(illegal_rows)} illegal rows."
                logger.warning(msg)
                for row in illegal_rows:
                    linenumber = row.get("linenumber", "Unknown")
                    error_txt = row.get("error", "Exception")
                    line_highlighted = row.get("line_highlighted", "")
                    msg = f"Line {linenumber}: {line_highlighted} # {error_txt}"
                    logger.warning(msg)
            if errors == "raise" and illegal_rows:
                raise ValueError("Illegal/Il-defined hole detected!")
        else:
            hole = Hole()
        hole.add_header("OM", {"Owner": line.get("properties", dict()).get("OMISTAJA", "-")})

        x, y = line["geometry"]["coordinates"]
        x, y = round(float(y), 10), round(float(x), 10)
        if not hasattr(hole.header, "XY"):
            file_xy = {"X": None, "Y": None}
            hole.add_header("XY", file_xy)
        hole.header.XY["X"], hole.header.XY["Y"] = x, y  # pylint: disable=E1101
        file_fo = {"Format version": "?", "Software": "GTK_WFS"}
        hole.add_fileheader("FO", file_fo)
        file_kj = {
            "Coordinate system": "WGS84",
            "Height reference": line["properties"]["KORKEUSJARJ"],
        }
        hole.add_fileheader("KJ", file_kj)
        return hole

    startindex = 0
    while len(holes) < maxholes:
        wfs_io = wfs.getfeature(
            typename=["Rajapinnat_GTK_Pohjatutkimukset_WFS:Pohjatutkimukset"],
            bbox=bbox,
            maxfeatures=page_size,
            startindex=startindex,
            outputFormat="GEOJSON",
        )
        data = wfs_io.read()
        # This is too slow, tested usually as utf-8
        # encoding_dict = chardet.detect(data)
        # data = data.decode(encoding=encoding_dict.get("encoding", "UTF-8"), errors="replace")
        data = data.decode("UTF-8", errors="replace")
        data = (
            data.replace("\\", r"\\")
            .replace("strenght", "strength")
            .replace("Strenght", "Strength")
        )
        while True:
            try:
                data_json = json.loads(data, strict=False)
                break
            except json.JSONDecodeError as error:
                if error.msg == "Expecting ',' delimiter":
                    msg = (
                        f"JSONDecodeError: {error.msg} at pos {error.pos}."
                        " Assuming invalid char, replacing \" with '."
                    )
                    logger.warning(msg)
                    data = data[: error.pos - 1] + "'" + data[error.pos :]
        if "features" in data_json:
            i = startindex
            if len(data_json["features"]) == 0:
                break
            for line in data_json["features"]:
                hole = None
                try:
                    hole = parse_line(line)
                except KeyError as error:
                    msg = "Wfs hole parse failed, line {}. Missing {}".format(i, error)
                    logger.warning(msg)
                if hole:
                    holes.append(hole)
                    if progress_bar:
                        pbar.update(1)
                i += 1
                if len(holes) >= maxholes:
                    break
        else:
            msg = f"No features returned at page {startindex//page_size}."
            logger.warning(msg)
            break
        startindex += page_size
    if progress_bar:
        pbar.close()
    if collected_illegals and save_ignored:
        if isinstance(save_ignored, str):
            with open(save_ignored, "a") as f:
                if errors == "ignore_holes":
                    write_fileheader(holes, f, fo=None, kj=None)
                f.write("\n".join(collected_illegals))
        else:
            if errors == "ignore_holes":
                write_fileheader(holes, save_ignored, fo=None, kj=None)
            print("\n".join(collected_illegals), file=save_ignored)
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
    with _open(path, mode=write_mode) as f:
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
            line = " ".join(line_string) + "\n"
            f.write(line)


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
            line = " ".join(header_string) + "\n"
            f.write(line)


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
        items = []
        labs = []
        for key, value in line_dict.items():
            if "Laboratory" in key:
                lab_type = key.rsplit(" ", 1)[-1]
                lab_line = f"LB {lab_type} {value}"
                labs.append(lab_line)
            elif "Sieve" in key:
                lab_type = key.rsplit(" ", 1)[-1]
                lab_line = f"RK {lab_type} {value}"
                labs.append(lab_line)
            elif key != "linenumber":
                items.append(str(value))
        line_string = body_spacer_start + "{}".format(body_spacer).join(items)
        for lab_line in sorted(labs):
            line_string += "\n" + lab_line
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
        ending_line = " ".join([str(ending[key]) for key in ending if key != "linenumber"])
        linenumber = max(body_text.keys()) + 1 if len(body_text) > 0 else 1
        body_text[float(linenumber)] = "-1 " + ending_line

    # print to file
    for key in sorted(body_text.keys()):
        line = body_text[key] + "\n"
        f.write(line)


@contextmanager
def _open(path, *args, **kwargs):
    """Yield StringIO or BytesIO if needed."""
    if hasattr(path, "write") or hasattr(path, "read"):
        try:
            yield path
        finally:
            pass
    else:
        with io.open(path, *args, **kwargs) as f:
            yield f


def read(path, encoding="auto", errors="ignore_lines", save_ignored=False):
    """Read input data.

    Paramaters
    ----------
    path : str, optional, default None
        path to read data (file / folder / glob statement, see use_glob)
    encoding : str, optional, default 'auto'
    errors : 'ignore_lines', 'ignore_holes', 'force' or 'raise', default 'ignore_lines'
        How to handle ill-defined/illegal lines or holes.
        'force' forces ill-defined values as str and adds error,
        'ignore_lines' passes line as a whole if there is ill-defined values.
    save_ignored : str, StringIO or False, default False
        Append ignored holes or lines to a file. File path str or
        a file-like object (stream) into built-in print function 'file' parameter.
    """
    if errors not in {"ignore_lines", "ignore_holes", "raise", "force"}:
        msg = "Argument errors must be 'ignore_lines', 'ignore_holes', 'raise' or 'force'."
        raise ValueError(msg)
    collected_illegals = []

    file_header_identifiers, *_ = identifiers()

    fileheaders = {}
    fileheader_raw = []
    fileheader_illegals = []
    holes = []

    with _open(path, "rb") as file:
        text_bytes = file.read()
    if isinstance(text_bytes, bytes):
        if encoding == "auto":
            encoding_dict = chardet.detect(text_bytes)
            lines = text_bytes.decode(
                encoding=encoding_dict.get("encoding", "ascii"), errors="replace"
            ).splitlines()
        else:
            lines = text_bytes.decode(encoding=encoding).splitlines()
    else:
        lines = text_bytes.splitlines()

    holestr_list = []
    for linenumber, line in enumerate(lines):
        if not line.strip():
            continue
        head, *tail = line.split(maxsplit=1)
        # Check if head is fileheader
        if head.upper() in file_header_identifiers:
            fileheader, line_errors = dictify_line(
                line, head=head.upper(), restrict_fields=True, force=False
            )
            fileheaders[head.upper()] = fileheader
            fileheader_raw.append(line)
            fileheader_illegals.extend(line_errors)
            for row in line_errors:
                linenumber = row.get("linenumber", "Unknown")
                error_txt = row.get("error", "Exception")
                line_highlighted = row.get("line_highlighted", "")
                msg = f"Line {linenumber}: {line_highlighted} # {error_txt}"
                logger.warning(msg)

        # make this robust check with peek
        elif head == "-1":
            if errors == "ignore_holes":
                try:
                    hole, illegal_rows = parse_hole(holestr_list, force=False)
                except ValueError:
                    collected_illegals.extend(holestr_list)
                    hole = Hole()
                    illegal_rows = None
            elif errors in {"ignore_lines", "raise"}:
                hole, illegal_rows = parse_hole(holestr_list, force=False)
                collected_illegals.extend(illegal_rows)
            elif errors == "force":
                hole, illegal_rows = parse_hole(holestr_list, force=True)
                collected_illegals.extend(illegal_rows)

            if illegal_rows:
                hole_id = hole.get("header_XY_Point ID", "-")
                index = len(holes) if hole else "-"
                msg = f"Hole {index} / Point ID: {hole_id} has {len(illegal_rows)} illegal rows."
                logger.warning(msg)
                for row in illegal_rows:
                    linenumber = row.get("linenumber", "Unknown")
                    error_txt = row.get("error", "Exception")
                    line_highlighted = row.get("line_highlighted", "")
                    msg = f"Line {linenumber}: {line_highlighted} # {error_txt}"
                    logger.warning(msg)
            if illegal_rows and errors == "raise":
                raise ValueError("Illegal/Il-defined hole detected!")

            # Add fileheaders to hole objects
            if fileheaders:
                for key, value in fileheaders.items():
                    hole.add_fileheader(key, value)
                hole.fileheader.raw_str = "\n".join(fileheader_raw)
            if fileheader_illegals:
                hole.fileheader.illegals.extend(fileheader_illegals)
            if tail:
                hole.add_header("-1", {"Ending": tail[0].strip()})
            holes.append(hole)
            holestr_list = []
        else:
            holestr_list.append((linenumber, line.strip()))

    # Check if '-1' is not the last line
    hole = None
    if holestr_list:
        logger.warning("File has to end on -1 row.")
        if errors == "ignore_holes":
            hole, illegal_rows = parse_hole(holestr_list, force=False)
            if illegal_rows:
                collected_illegals.extend(holestr_list)
                hole = None
        elif errors in {"ignore_lines", "raise"}:
            hole, illegal_rows = parse_hole(holestr_list, force=False)
            collected_illegals.extend(illegal_rows)
        elif errors == "force":
            hole, illegal_rows = parse_hole(holestr_list, force=True)
            collected_illegals.extend(illegal_rows)
        if illegal_rows:
            hole_id = hole.get("header_XY_Point ID", "-")
            index = len(holes) if hole else "-"
            msg = f"Hole {index} / Point ID: {hole_id} has {len(illegal_rows)} illegal rows."
            logger.warning(msg)
            for row in illegal_rows:
                linenumber = row.get("linenumber", "Unknown")
                error_txt = row.get("error", "Exception")
                line_highlighted = row.get("line_highlighted", "")
                msg = f"Line {linenumber}: {line_highlighted} # {error_txt}"
                logger.warning(msg)

        if errors == "raise":
            raise ValueError("File has to end on -1 row.")
        if fileheaders and hole:
            for key, value in fileheaders.items():
                hole.add_fileheader(key, value)
        if fileheader_illegals and hole:
            hole.fileheader.illegals.extend(fileheader_illegals)
        holestr_list = []
        if hole:
            holes.append(hole)

    if collected_illegals and save_ignored:
        if isinstance(save_ignored, str):
            with open(save_ignored, "a") as f:
                if errors == "ignore_holes":
                    write_fileheader(holes, f, fo=None, kj=None)
                f.write("\n".join(collected_illegals))
        else:
            if errors == "ignore_holes":
                write_fileheader(holes, save_ignored, fo=None, kj=None)
            print("\n".join(collected_illegals), file=save_ignored)

    return holes


def split_with_whitespace(string, maxsplit=None):
    """Split string with whitespaces, maxsplit defines maximum non white-space items.

    >>> split_with_whitespace("   This is an example", maxsplit=2)
    ['', '   ', 'This', ' ', 'is an example']
    """
    return_string = []
    last_item = []
    count = 0
    splitted = re.split(r"(\s+)", string)
    if maxsplit is None or maxsplit < 0:
        return splitted
    if maxsplit == 0:
        return [string]
    for item in splitted:
        if not str.isspace(item) and item:
            count += 1
        if count >= maxsplit:
            last_item.append(item)
        else:
            return_string.append(item)
    return return_string + ["".join(last_item)]


def highlight_item(string, indexes=None, marker="**", maxsplit=None):
    """Hightlight string items with by split_with_whitespace indexes.

    Examples
    --------
    >>> highlight_item("   Yeah this is an example", [2,6], marker="**")
    '     **Yeah**   this   **is**   an   example'
    """
    if isinstance(indexes, int):
        indexes = [indexes]
    if indexes is None:
        return marker + string + marker
    if all(item is None for item in indexes):
        return marker + string + marker
    highlighted = []
    for i, value in enumerate(split_with_whitespace(string, maxsplit)):
        if i in set(indexes):
            highlighted.append(marker + value + marker)
        else:
            highlighted.append(value)
    return "".join(highlighted)


def dictify_line(line, head=None, restrict_fields=True, force=False):
    """Parse line into dict as infraformat line.

    Returns
    -------
    line_dict : dict
        line values parsed to dict
    line_errors : list
        (error_string, 'split_with_whitespace' index)
    """
    if head is None:
        head = line.split()[0].strip()
    (
        file_header_identifiers,
        header_identifiers,
        inline_identifiers,
        survey_identifiers,
    ) = identifiers()
    if head in file_header_identifiers:
        names, dtypes, strict = file_header_identifiers[head]
    elif head in header_identifiers:
        names, dtypes, strict = header_identifiers[head]
    elif head in inline_identifiers:
        names, dtypes, strict = inline_identifiers[head]
    elif head in survey_identifiers:
        if head != "HP":
            names, dtypes, strict = survey_identifiers[head]
        # HP survey is a special case
        else:
            survey_dict = survey_identifiers[head]
            if any(item.upper() == "H" for item in line.split()):
                names, dtypes, strict = survey_dict["H"]
            else:
                names, dtypes, strict = survey_dict["P"]
    else:
        raise ValueError(f"Head '{head}' not recognized")

    maxsplit = len(dtypes)
    if head.upper() == line.split()[0].strip().upper():
        maxsplit += 1
    line_splitted = split_with_whitespace(line, maxsplit=maxsplit if restrict_fields else None)
    count = 0
    line_dict = {}
    line_errors = []

    items = [item for item in enumerate(line_splitted) if item[1] and not str.isspace(item[1])]
    if items[0][1] == head:
        items = items[1:]
    for index, value in items:
        if count >= len(names):
            line_errors.append(("Line has too many values", index))
        else:
            key = names[count]
            value_type = dtypes[count]
            mandatory = strict[count]
            value = value.strip()
            if is_nan(value):
                if mandatory:
                    line_errors.append((f"Value for '{key}' is mandatory", index))
                if force:
                    line_dict[key] = "-"
            else:
                try:
                    line_dict[key] = value_type(value)
                except ValueError:
                    value_name = str(value_type.__name__)
                    msg = f"Could not convert '{key}' value '{value}' to '{value_name}'."
                    line_errors.append((msg, index))
                    if force:
                        line_dict[key] = str(value)
            count += 1
    while count < len(dtypes):
        key = names[count]
        mandatory = strict[count]
        if mandatory:
            line_errors.append((f"Value for '{key}' is mandatory!", None))
        count += 1

    return line_dict, line_errors


def strip_header(line, head=None, restrict_fields=True, force=False):
    """Strip header line, returns (hole, error_dict).

    Examples
    --------
    >>> header_dict, errors = strip_header("XY 6674772.0 NOT_COORD 15.0 01011999 1")
    >>> errors
    {'error': "1. Could not convert 'Y' value 'NOT_COORD' to 'custom_float'.",
     'line_highlighted': 'XY 6674772.0 **NOT_COORD** 15.0 01011999 1'}
    """
    if head is None:
        head = line.split()[0].strip()
    header, line_errors = dictify_line(line, head, restrict_fields, force=force)

    error_dict = {}
    if line_errors:
        line_highlighted = highlight_item(line, [index for _, index in line_errors], marker="**")
        error_full = ", ".join(
            [f"{i}. {item}" for i, item in enumerate([error for error, _ in line_errors], start=1)]
        )
        error_dict = {
            "error": error_full,
            "line_highlighted": line_highlighted,
        }

    return header, error_dict


def strip_inline(line, head=None, restrict_fields=True, force=False):
    """Strip inline line, returns (hole, error_dict).

    Examples
    --------
    >>> strip_inline("LB w 12 kg/m3")
    ({'Laboratory w': '12'}, {})
    """
    if head is None:
        head = line.split()[0].strip()
    inline, line_errors = dictify_line(line, head, restrict_fields, force=force)

    error_dict = {}
    if line_errors:
        line_highlighted = highlight_item(line, [index for _, index in line_errors], marker="**")
        error_full = ", ".join(
            [f"{i}. {item}" for i, item in enumerate([error for error, _ in line_errors], start=1)]
        )
        error_dict = {
            "error": error_full,
            "line_highlighted": line_highlighted,
        }
    if head == "LB":
        if ("Laboratory" in inline) and ("Result" in inline):
            lab_test = {f"Laboratory {inline['Laboratory']}": inline["Result"]}
            # test if inline["test type"] is not number
            return lab_test, error_dict
    elif head == "RK":
        if ("Sieve size" in inline) and ("Passing percentage" in inline):
            lab_test = {f"Sieve {inline['Sieve size']}": inline["Passing percentage"]}
            return lab_test, error_dict
    return inline, error_dict


def strip_survey(line, survey_type, restrict_fields=True, force=False):
    """Strip survey line as survey_type, returns (hole, error_dict).

    Examples
    --------
    >>> strip_survey("     1.50   42  Ka", "PO")
    ({'Depth (m)': 1.5, 'Time (s)': 42, 'Soil type': 'Ka'}, {})
    """
    *_, survey_identifiers = identifiers()
    if survey_type not in survey_identifiers:
        error_dict = {
            "error": f"Cannot parse survey as survey identifier '{survey_type}' is invalid.",
            "line_highlighted": highlight_item(line, indexes=None),
        }
        return (None, error_dict)

    survey, line_errors = dictify_line(line, survey_type, restrict_fields, force=force)
    error_dict = {}
    if line_errors:
        line_highlighted = highlight_item(line, [index for _, index in line_errors], marker="**")
        error_full = ", ".join(
            [f"{i}. {item}" for i, item in enumerate([error for error, _ in line_errors], start=1)]
        )
        error_dict = {
            "error": error_full,
            "line_highlighted": line_highlighted,
        }
    return survey, error_dict


def parse_hole(str_list, force=False):
    """Parse inframodel lines to hole objects.

    Paramaters
    ----------
    str_list : list
        lines as enumerated list of strings
    force : bool
        Whetere to force illegal values as str. Ex. illegal dates, floats, int
        will be represented as str. Else omitted. Both cases gathered as errors.

    Return
    ------
    Hole -object
    errors : list
        List of dicts with keys {linenumber, error, line_highlighted}.
        ex. [{"linenumber" : 11, "error" :"Line not recognized!",
                "line_highlighted" : "**rivit tietoa ja silee jossa ei järkeä**" },
            {"linenumber" : 13, "error" : "Value must be float!, Date must be format ddmmyyy!",
            "line_highlighted" : "XY **x_koordinaatti** 999 **12345678** piste22" }
    """
    str_list = list(str_list)
    errors = []

    _, header_identifiers, inline_identifiers, _ = identifiers()

    hole = Hole()
    hole.raw_str = "\n".join([line for _, line in str_list])
    survey_type = None
    for linenumber, line in str_list:
        if not line.strip():
            continue
        head, *_ = line.split(maxsplit=1)
        head = head.upper()

        if survey_type is None and hasattr(hole.header, "TT"):
            survey_type = getattr(hole.header, "TT").get("Survey abbreviation", None)
            if survey_type:
                survey_type = survey_type.upper()

        try:
            if head in header_identifiers:
                header, error_dict = strip_header(line, head, force=force)
                header["linenumber"] = linenumber
                if error_dict:
                    error_dict["linenumber"] = linenumber
                    hole.illegals.append(error_dict)
                    errors.append(error_dict)
                hole.add_header(head, header)
            elif head in inline_identifiers:
                inline, error_dict = strip_inline(line, head, force=force)
                inline["linenumber"] = linenumber
                if error_dict:
                    error_dict["linenumber"] = linenumber
                    hole.illegals.append(error_dict)
                    errors.append(error_dict)
                if head in {"LB", "RK"}:  # LB and RK are connected to last survey row
                    if len(hole.survey.data) > 0 and inline:
                        hole.survey[-1].update(inline)
                    else:
                        error_dict = {
                            "linenumber": linenumber,
                            "error": "LB inline without previous data!",
                            "line_highlighted": highlight_item(line, None),
                        }
                        errors.append(error_dict)
                else:
                    hole.add_inline(head, inline)
            elif (is_number(head) and survey_type) or survey_type in ("LB",):
                survey, error_dict = strip_survey(line, survey_type, force=force)
                if error_dict:
                    error_dict["linenumber"] = linenumber
                    hole.illegals.append(error_dict)
                    errors.append(error_dict)
                if survey:
                    survey["linenumber"] = linenumber
                    hole.add_survey(survey)
            else:
                error_dict = {
                    "linenumber": linenumber,
                    "error": "Line not recognized!",
                    "line_highlighted": highlight_item(line, None),
                }
                hole.illegals.append(error_dict)
                errors.append(error_dict)
        except (ValueError, KeyError) as error:
            # import traceback

            # traceback.print_exc()
            error = str(repr(error))
            logger.warning("Unexpected error %s", error)
            error_dict = {
                "linenumber": linenumber,
                "error": error,
                "line_highlighted": highlight_item(line, None),
            }

            hole.illegals.append(error_dict)
            errors.append(error_dict)
    return hole, errors
