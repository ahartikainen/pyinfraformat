"""Input and output methods."""
from collections import Counter
from glob import glob
import logging
import os
from .exceptions import PathNotFoundError
from .parser import read, identifiers

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
    from .core import Holes  # pylint: disable=cyclic-import

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


def to_infraformat(data, path, comments=True, fo=None, kj=None):
    """Export data to infraformat.

    Parameters
    ----------
    data : list
        a list containing hole data
    path : str
        path to save data
    fo : dict
        dictionary for fileformat
        contains
            'Format version', default 2.3
            'Software', default 'pyInfraformat'
            'Software version', default 'str(__version__)'
    kj : dict
        dictionary  for coordinate system
        contains
            'Coordinate system', default mode(data)
            'Height reference', default mode(data)
        default mode of the holes
    """
    with open(path, mode="w") as f:
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
        from .__init__ import __version__

        fo = {
            "Format version": "2.3",
            "Software": "pyInfraformat",
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
            line_string.append(str(value))
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
def write_body(hole, f, comments=True, illegal=False):
    """Write data out.

    Parameters
    ----------
    hole : Hole object
    f : fileobject
    comments : bool
    illegal : bool
    """
    body_text = {}
    # Gather survey information
    line_dict = {}
    for line_dict in hole.survey.data:
        line_string = " ".join(
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
