""".tek -file parsing submodule."""
from datetime import datetime
import logging
import numpy as np
import pandas as pd

from .utils import identifiers, is_number

logger = logging.getLogger("pyinfraformat")

__all__ = []


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


class Hole:
    """Class to hold Hole information."""

    def __init__(self):
        self.fileheader = FileHeader()
        self.header = Header()
        self.inline_comment = InlineComment()
        self.survey = Survey()
        self._illegal = Illegal()

    def __str__(self):
        from pprint import pformat

        msg = pformat(self.header.__dict__)
        return f"Infraformat Hole -object:\n  {msg}"

    def __repr__(self):
        return self.__str__()

    def add_fileheader(self, key, fileheader):
        """Add fileheader to object."""
        self.fileheader.add(key, fileheader)

    def add_header(self, key, header):
        """Add header to object."""
        self.header.add(key, header)

    def add_inline_comment(self, key, comment):
        """Add inline comment to object."""
        self.inline_comment.add(key, comment)

    def add_survey(self, survey):
        """Add survey information to object."""
        self.survey.add(survey)

    def _add_illegal(self, illegal):
        """Add illegal lines to object."""
        self._illegal.add(illegal)

    @property
    def dataframe(self):
        """Create pandas.DataFrame."""
        return self._get_dataframe(update=False)

    def _get_dataframe(self, update=False):
        """Get pandas.DataFrame object.

        Creates a new pandas.DataFrame if it doesn't exists of update is True

        Paramaters
        ----------
        update : None or bool, optional, default None
            None
                Return earlier pandas.DataFrame if it exists and adds automatically new data
            False
                Return earlier pandas.DataFrame if it exists
            True
                Calculate a new pandas.DataFrame
        """
        if hasattr(self, "_dataframe") and not update:
            return self._dataframe  # pylint: disable=access-member-before-definition

        dict_list = self.survey.data
        self._dataframe = pd.DataFrame(dict_list)  # pylint: disable=attribute-defined-outside-init
        self._dataframe.columns = ["data_{}".format(col) for col in self._dataframe.columns]
        if not self._dataframe.empty:
            self._dataframe.loc[0, self._dataframe.columns] = np.nan
        for key in self.header.keys:
            self._dataframe.loc[:, "Date"] = self.header.date
            for key_, item in getattr(self.header, key).items():
                self._dataframe.loc[:, "header_{}_{}".format(key, key_)] = item
        for key in self.fileheader.keys:
            for key_, item in getattr(self.fileheader, key).items():
                self._dataframe.loc[:, "fileheader_{}_{}".format(key, key_)] = item

        return self._dataframe


class FileHeader:
    """Class to hold file header information."""

    def __init__(self):
        self.keys = set()

    def add(self, key, values):
        """Add member to class."""
        setattr(self, key, values)
        self.keys.add(key)

    def __str__(self):
        msg = f"FileHeader object - Fileheader contains {len(self.keys)} items"
        return msg

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, attr):
        if attr in self.keys:
            return getattr(self, attr)
        else:
            raise TypeError("Attribute not found: {}".format(attr))


# pylint: disable=too-few-public-methods
class Header:
    """Class to hold header information."""

    def __init__(self):
        self.keys = set()
        self.date = pd.NaT

    def add(self, key, values):
        """Add header items to object."""
        if key == "XY" and ("Date" in values):
            if len(values["Date"]) == 6:
                date = datetime.strptime(values["Date"], "%d%m%y")
            elif len(values["Date"]) == 8:
                date = datetime.strptime(values["Date"], "%d%m%Y")
            else:
                try:
                    date = pd.to_datetime(values["Date"])
                except ValueError:
                    date = pd.NaT
            self.date = date
        setattr(self, key, values)
        self.keys.add(key)

    def __getitem__(self, attr):
        if attr in self.keys:
            return getattr(self, attr)
        else:
            raise TypeError("Attribute not found: {}".format(attr))


# pylint: disable=too-few-public-methods
class InlineComment:
    """Class to inline comments."""

    def __init__(self):
        self.data = list()

    def add(self, key, values):
        """Add inline comments to object."""
        self.data.append((key, values))

    def __getitem__(self, attr):
        return self.data[attr]


# pylint: disable=too-few-public-methods
class Survey:
    """Class to survey information."""

    def __init__(self):
        self.data = list()

    def add(self, values):
        """Add survey information to object."""
        self.data.append(values)

    def __getitem__(self, attr):
        return self.data[attr]


# pylint: disable=too-few-public-methods
class Illegal:
    """Class to contain illegal lines."""

    def __init__(self):
        self.data = list()

    def add(self, values):
        """Add illegal lines to object."""
        self.data.append(values)

    def __getitem__(self, attr):
        return self.data[attr]
