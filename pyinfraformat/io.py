from collections import Counter
from .parser import identifiers

# import pyproj


def to_infraformat(data, path, comments=True, fo=None, kj=None):
    """
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
    if fo is None:
        from .__init__ import __version__

        fo = {
            "Format version": "2.3",
            "Software": "pyInfraformat",
            "Software version": str(__version__),
        }
    if kj is None:
        # TODO: add coord transformations
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
    """
    header : header object
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
            for key, value in attr.items():
                if key == "linenumber":
                    continue
                header_string.append(str(value))
            print(" ".join(header_string), file=f)


def write_body(hole, f, comments=True, illegal=False):
    """
    hole : Hole object
    f : fileobject
    comments : bool
    illegal : bool
    """
    body_text = {}
    # Gather survey information
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
