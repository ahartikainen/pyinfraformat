""".tek -file parsing submodule."""
from datetime import datetime
import logging
import numpy as np
import pandas as pd  # pd.DataFrame, pd.NaT

logger = logging.getLogger("pyinfraformat")

__all__ = ["identifiers"]


def _is_number(number_str):
    """Test if number_str is number."""
    try:
        complex(number_str)
    except ValueError:
        if number_str == "-":
            return True
        return False
    return True


def custom_int(number):
    """Test if number is integer."""
    try:
        return int(number)
    except ValueError:
        if number == "-":
            return np.nan
        if int(float(number)) == float(number):
            return int(float(number))
        else:
            msg = "Non-integer value detected, a floating point number is returned"
            logger.warning(msg)
            return float(number)


def custom_float(number):
    """Test if number is floating point number."""
    if number.strip() == "-":
        return np.nan
    else:
        try:
            return float(number)
        except ValueError:
            return np.nan


def identifiers():
    """ helper function to return header identifiers.

        returns a tuple:
            file_header_identifiers,
            header_identifiers, ,
            inline_identifiers,
            survey_identifiers,

    """
    file_header_identifiers = {
        "FO": (["Format version", "Software", "Software version"], [str, str, str]),
        "KJ": (["Coordipd.NaTe system", "Height reference"], [str, str]),
    }

    # point specific
    header_identifiers = {
        "OM": (["Owner"], [str]),
        "ML": (["Soil or rock classification"], [str]),
        "OR": (["Research organization"], [str]),
        "TY": (["Work number", "Work name"], [str, str]),
        "PK": (["Record number", "Driller", "Inspector", "Handler"], [custom_int, str, str, str]),
        "TT": (
            ["Survey abbreviation", "Class", "ID1", "Used standard", "Sampler"],
            [str, custom_int, str, str, str],
        ),
        "LA": (["Device number", "Device description text"], [custom_int, str]),
        "XY": (
            ["X", "Y", "Z-start", "Date", "ID2"],
            [custom_float, custom_float, custom_float, str, str],
        ),
        "LN": (["Line name or number", "Pole", "Distance"], [str, custom_float, custom_float]),
        "-1": (["Ending"], [str]),
        "GR": (["Software name", "Date", "Programmer"], [str, str, str]),
        "GL": (["Survey info"], [str]),
        "AT": (["Rock sample attribute", "Possible value"], [str, str]),
        "AL": (
            ["Initial boring depth", "Initial boring method", "Initial boring soil type"],
            [custom_float, str, str],
        ),
        "ZP": (
            ["ZP1", "ZP2", "ZP3", "ZP4", "ZP5"],
            [custom_float, custom_float, custom_float, custom_float, custom_float],
        ),
        "TP": (["TP1", "TP2", "TP3", "TP4", "TP5"], [str, custom_float, str, str, str]),
        "LP": (["LP1", "LP2", "LP3", "LP4", "LP5"], [str, str, str, str, str]),
    }
    # line specific
    # inline comment / info
    inline_identifiers = {
        "HM": (["obs"], [str]),
        "TX": (["free text"], [str]),
        "HT": (["hidden text"], [str]),
        "EM": (["Unofficial soil type"], [str]),
        "VH": (["Water level observation"], []),
        "KK": (
            ["Azimuth (degrees)", "Inclipd.NaTion (degrees)", "Diameter (mm)"],
            [custom_float, custom_float, custom_int],
        ),
    }

    # datatypes
    # most contain tuple (column_names, column_dtype)
    # 1 dictionary for 'HP'
    survey_identifiers = {
        "PA/WST": (
            ["Depth (m)", "Load (kN)", "Rotation of half turns (-)", "Soil type"],
            [custom_float, custom_float, custom_int, str],
        ),
        "PA": (
            ["Depth (m)", "Load (kN)", "Rotation of half turns (-)", "Soil type"],
            [custom_float, custom_float, custom_int, str],
        ),
        "WST": (
            ["Depth (m)", "Load (kN)", "Rotation of half turns (-)", "Soil type"],
            [custom_float, custom_float, custom_int, str],
        ),
        "PI": (["Depth (m)", "Soil type"], [custom_float, str]),
        "LY": (
            ["Depth (m)", "Load (kN)", "Blows", "Soil type"],
            [custom_float, custom_float, custom_int, str],
        ),
        "SI/FVT": (
            [
                "Depth (m)",
                "Shear strenght (kN/m^2)",
                "Residual Shear strenght (kN/m^2)",
                "Sensitivity (-)",
                "Residual strenght (MPa)",
            ],
            [custom_float, custom_float, custom_float, custom_float, custom_float],
        ),
        "SI": (
            [
                "Depth (m)",
                "Shear strenght (kN/m^2)",
                "Residual Shear strenght (kN/m^2)",
                "Sensitivity (-)",
                "Residual strenght (MPa)",
            ],
            [custom_float, custom_float, custom_float, custom_float, custom_float],
        ),
        "FVT": (
            [
                "Depth (m)",
                "Shear strenght (kN/m^2)",
                "Residual Shear strenght (kN/m^2)",
                "Sensitivity (-)",
                "Residual strenght (MPa)",
            ],
            [custom_float, custom_float, custom_float, custom_float, custom_float],
        ),
        "HE/DP": (["Depth (m)", "Blows", "Soil type"], [custom_float, custom_int, str]),
        "HE": (["Depth (m)", "Blows", "Soil type"], [custom_float, custom_int, str]),
        # 'DP' : (),
        "HK/DP": (
            ["Depth (m)", "Blows", "Torque (Nm)", "Soil type"],
            [custom_float, custom_int, custom_float, str],
        ),
        "HK": (
            ["Depth (m)", "Blows", "Torque (Nm)", "Soil type"],
            [custom_float, custom_int, custom_float, str],
        ),
        # 'DP' : (),
        "PT": (["Depth (m)", "Soil type"], [custom_float, str]),
        "TR": (["Depth (m)", "Soil type"], [custom_float, str]),
        "PR": (
            ["Depth (m)", "Total resistance (MN/m^2)", "Sleeve friction (kN/m^2)", "Soil type"],
            [custom_float, custom_float, custom_float, str],
        ),
        "CP/CPT": (
            [
                "Depth (m)",
                "Total resistance (MN/m^2)",
                "Sleeve friction (kN/m^2)",
                "Cone resistance (MN/m^2)",
                "Soil type",
            ],
            [custom_float, custom_float, custom_float, custom_float, str],
        ),
        "CP": (
            [
                "Depth (m)",
                "Total resistance (MN/m^2)",
                "Sleeve friction (kN/m^2)",
                "Cone resistance (MN/m^2)",
                "Soil type",
            ],
            [custom_float, custom_float, custom_float, custom_float, str],
        ),
        "CPT": (
            [
                "Depth (m)",
                "Total resistance (MN/m^2)",
                "Sleeve friction (kN/m^2)",
                "Cone resistance (MN/m^2)",
                "Soil type",
            ],
            [custom_float, custom_float, custom_float, custom_float, str],
        ),
        "CU/CPTU": (
            [
                "Depth (m)",
                "Total resistance (MN/m^2)",
                "Sleeve friction (kN/m^2)",
                "Cone resistance (MN/m^2)",
                "Pore pressure (kN/m^2)",
                "Soil type",
            ],
            [custom_float, custom_float, custom_float, custom_float, custom_float, str],
        ),
        "CU": (
            [
                "Depth (m)",
                "Total resistance (MN/m^2)",
                "Sleeve friction (kN/m^2)",
                "Cone resistance (MN/m^2)",
                "Pore pressure (kN/m^2)",
                "Soil type",
            ],
            [custom_float, custom_float, custom_float, custom_float, custom_float, str],
        ),
        "CPTU": (
            [
                "Depth (m)",
                "Total resistance (MN/m^2)",
                "Sleeve friction (kN/m^2)",
                "Cone resistance (MN/m^2)",
                "Pore pressure (kN/m^2)",
                "Soil type",
            ],
            [custom_float, custom_float, custom_float, custom_float, custom_float, str],
        ),
        "HP": {
            "H": (
                ["Depth (m)", "Blows", "Torque (Nm)", "Survey type", "Soil type"],
                [custom_float, custom_int, custom_float, str, str],
            ),
            "P": (
                ["Depth (m)", "Pressure (MN/m^2)", "Torque (Nm)", "Survey type", "Soil type"],
                [custom_float, custom_float, custom_float, str, str],
            ),
        },
        "PO": (["Depth (m)", "Time (s)", "Soil type"], [custom_float, custom_int, str]),
        "MW": (
            [
                "Depth (m)",
                "Speed (cm/min)",
                "Compressive force (kN)",
                "MW4",
                "MW5",
                "Torque (Nm)",
                "Rotational speed (rpm)",
                "Blow",
                "Soil type",
            ],
            [
                custom_float,
                custom_float,
                custom_float,
                custom_float,
                custom_float,
                custom_float,
                custom_float,
                str,
                str,
            ],
        ),
        "VP": (
            [
                "Water level",
                "Date",
                "Top level of pipe",
                "Bottom level of pipe",
                "Lenght of the sieve(m)",
                "Inspector",
            ],
            [custom_float, str, custom_float, custom_float, custom_float, str],
        ),
        "VO": (
            [
                "Water level",
                "Date",
                "Top level of pipe",
                "Bottom level of pipe",
                "Lenght of the sieve(m)",
                "Inspector",
            ],
            [custom_float, str, custom_float, custom_float, custom_float, str],
        ),
        "VK": (["Water level", "Date", "Type"], [custom_float, str, str]),
        "VPK": (["Water level", "Date"], [custom_float, str]),
        "HV": (
            ["Depth (m)", "Pressure (kN/m^2)", "Date", "Measurer"],
            [custom_float, custom_float, str, str],
        ),
        "PS/PMT": (
            ["Depth (m)", "Pressometer modulus (MN/m^2)", "Burst pressure (MN/m^2)"],
            [custom_float, custom_float, custom_float],
        ),
        "PS": (
            ["Depth (m)", "Pressometer modulus (MN/m^2)", "Burst pressure (MN/m^2)"],
            [custom_float, custom_float, custom_float],
        ),
        "PMT": (
            ["Depth (m)", "Pressometer modulus (MN/m^2)", "Burst pressure (MN/m^2)"],
            [custom_float, custom_float, custom_float],
        ),
        "PM": (["Height", "Date", "Measurer"], [custom_float, str, str]),
        "KO": (
            ["Depth (m)", "Soil type", "rock", "rock", "Maximum width", "Minimum width"],
            [custom_float, str, custom_float, custom_int, custom_float, custom_float],
        ),
        "KE": (["Initial depth (m)", "Final depth (m)"], [custom_float, custom_float]),
        "KR": (["Initial depth (m)", "Final depth (m)"], [custom_float, custom_float]),
        "NO": (
            ["Depth  info 1 (m)", "Sample ID", "Depth info 2 (m)", "Soil type"],
            [custom_float, str, custom_float, str],
        ),
        "NE": (
            ["Depth info 1 (m)", "Sample ID", "Depth info 2 (m)", "Soil type"],
            [custom_float, str, custom_float, str],
        ),
        "LB": (["Laboratory", "Result", "Unit"], [str, str, str]),
        "RK": (["Sieve size", "Passing percentage"], [custom_float, custom_float]),
    }
    # common_survey_mistakes = {'KK' : ['KE', 'KR'],
    #                          'DP' : ['HE', 'HK']}

    result_tuple = (
        file_header_identifiers,
        header_identifiers,
        inline_identifiers,
        survey_identifiers,
        # common_survey_mistakes
    )
    return result_tuple


def read(path, encoding="utf-8"):
    """Helper function for read.

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
    """Function parse inframodel lines to hole objects.

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
            elif _is_number(head) and survey_type:
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
    """"Class to hold Hole information."""

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
        """
        Get pandas.DataFrame. Creates a new pandas.DataFrame if it doesn't exists of update is True

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
