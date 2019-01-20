"""Input and output methods."""
from collections import Counter
from glob import glob
import logging
import os
from .core import Holes, Hole
from ..exceptions import PathNotFoundError
from .utils import identifiers, is_number

logger = logging.getLogger("pyinfraformat")

__all__ = ["from_infraformat"]


def from_infraformat(path=None, encoding="utf-8", extension=None, robust_read=False):
    """Read inframodel file(s).

    Paramaters
    ----------
    path : str, optional, default None
        path to read data (file / folder / glob statement)
    encoding : str, optional, default 'utf-8'
        file encoding, if 'utf-8' fails, code will try to use 'latin-1'
    use_glob : bool, optional, default False
        path is a glob string
    extension : bool, optional, default None
    robust_read : bool, optional, default False
        Enable reading ill-defined holes

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

    hole_list = []
    if robust_read:
        if not hasattr(robust_read, "__iter__"):
            # Common encoding types
            robust_read = [
                "utf-8",
                "latin-1",
                "cp1252",
                "latin-6",
                "latin-2",
                "latin-3",
                "latin-5",
                "utf-16",
            ]
        for filepath in filelist:
            try:
                holes = read(filepath, encoding=encoding)
            except UnicodeDecodeError:
                holes = []
                for encoding_ in robust_read:
                    if encoding_ == encoding:
                        continue
                    try:
                        holes = read(filepath, encoding=encoding_)
                        break
                    except (UnicodeDecodeError, UnicodeEncodeError):
                        continue
            if holes:
                hole_list.extend(holes)
    else:
        for filepath in filelist:
            holes = read(filepath, encoding=encoding)
            hole_list.extend(holes)

    return Holes(hole_list)


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
            "Format version": "2.3",
            "Software": "pyinfraformat",
            "Software version": str(__version__),
        }
    if kj is None:
        # add coord transformations
        coord = []
        height = []
        for hole in data:
            if hasattr(hole.fileheader, "KJ"):
                coord.append(hole.fileheader.KJ["Coordinate system"])
                height.append(hole.fileheader.KJ["Height reference"])
        (coord, _), = Counter(coord).most_common()
        (height, _), = Counter(height).most_common()
        kj = {"Coordinate system": coord, "Height reference": height}

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
        body_spacer = "    "
    if body_spacer_start is None:
        body_spacer_start = "   "
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


def read(path, encoding="utf-8"):
    """Read input data.

    Paramaters
    ----------
    path : str, optional, default None
        path to read data (file / folder / glob statement, see use_glob)
    encoding : str, optional, default 'utf-8'
        file encoding, if 'utf-8' fails, code will try to use 'latin-1'
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
                names, dtypes = file_header_identifiers[head.upper()]
                fileheader = {key: format(value) for key, format, value in zip(names, dtypes, tail)}
                fileheaders[head.upper()] = fileheader
            # make this robust check with peek
            elif head == "-1":
                hole_object = parse_hole(holestr_list)
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
            hole_object = parse_hole(holestr_list)
            if fileheaders:
                for key, value in fileheaders.items():
                    hole_object.add_fileheader(key, value)
            holes.append(hole_object)
            holestr_list = []

    return holes


def parse_hole(str_list):
    """Parse inframodel lines to hole objects.

    Paramaters
    ----------
    str_list : list
        lines as list of strings
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

        try:
            if head in header_identifiers:
                names, dtypes = header_identifiers[head]
                if len(dtypes) == 1:
                    tail = [tail[0].strip()] if tail else []
                else:
                    tail = tail[0].strip().split() if tail else []
                header = {key: format(value) for key, format, value in zip(names, dtypes, tail)}
                header["linenumber"] = linenum
                hole.add_header(head, header)
            elif head in inline_identifiers:
                names, dtypes = inline_identifiers[head]
                if len(dtypes) == 1:
                    tail = [tail[0].strip()] if tail else []
                else:
                    tail = tail[0].strip().split() if tail else []
                inline_comment = {
                    key: format(value) for key, format, value in zip(names, dtypes, tail)
                }
                inline_comment["linenumber"] = linenum
                hole.add_inline_comment(head, inline_comment)
            elif is_number(head) and survey_type:
                if survey_type != "HP":
                    names, dtypes = survey_identifiers[survey_type]
                    line = line.split(maxsplit=len(dtypes))
                # HP survey is a special case
                else:
                    survey_dict = survey_identifiers[survey_type]
                    if any(item.upper() == "H" for item in line.split()):
                        names, dtypes = survey_dict["H"]
                    else:
                        names, dtypes = survey_dict["P"]

                    line = line.split(maxsplit=len(dtypes))
                survey = {key: format(value) for key, format, value in zip(names, dtypes, line)}
                survey["linenumber"] = linenum
                hole.add_survey(survey)
            else:
                # In future add warning
                hole._add_illegal((linenum, line))  # pylint: disable=protected-access
        except (ValueError, KeyError):
            # In future add warning
            hole._add_illegal((linenum, line))  # pylint: disable=protected-access
    return hole
