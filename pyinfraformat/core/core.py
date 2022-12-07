"""Core function for pyinfraformat."""
import fnmatch
import logging
import os
import pprint
from datetime import datetime
from numbers import Integral

import pandas as pd

from ..exceptions import FileExtensionMissingError

logger = logging.getLogger("pyinfraformat")

__all__ = ["Holes"]


class Holes:
    """Container for multiple infraformat hole information."""

    def __init__(self, holes=None, lowmemory=False):
        """Container for multiple infraformat hole information.

        Parameters
        ----------
        holes : list
            list of infraformat hole information
        lowmemory : bool, optional
            Create Pandas DataFrame one by one minimizing memory use.
        """
        if holes is None:
            holes = []
        self.holes = list(holes) if not isinstance(holes, Hole) else [holes]
        self._lowmemory = lowmemory
        self.n = None

    def __str__(self):
        msg = "Infraformat Holes -object:\n  Total of {n} holes".format(n=len(self.holes))
        value_counts = self.value_counts()
        if self.holes:
            max_length = max(len(str(values)) for values in value_counts.values()) + 1
            counts = "\n".join(
                "    - {key:.<10}{value:.>6}".format(
                    key="{} ".format(key),
                    value=("{:>" + "{}".format(max_length) + "}").format(value),
                )
                for key, value in value_counts.items()
            )
            msg = "\n".join((msg, counts))
        return msg

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, index):
        if isinstance(index, Integral):
            return self.holes[index]
        return Holes(self.holes[index])

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < len(self.holes):
            result = self.holes[self.n]
            self.n += 1
            return result
        else:
            raise StopIteration

    def __add__(self, other):
        if isinstance(other, Holes):
            return Holes(self.holes + other.holes)
        if isinstance(other, Hole):
            return Holes(self.holes + [other])
        raise ValueError("Only Holes or Hole -objects can be added.")

    def __len__(self):
        return len(self.holes)

    def append(self, hole):
        """Append Hole object to holes."""
        if isinstance(hole, Hole):
            self.holes += [hole]
        else:
            raise ValueError("Only Hole -object can be appended.")

    def extend(self, holes):
        """Extend with Holes -object."""
        if isinstance(holes, Holes):
            self.holes += holes
        else:
            raise ValueError("Only Holes -object can be extended.")

    def filter_holes(self, *, bbox=None, hole_type=None, start=None, end=None, fmt=None, **kwargs):
        """Filter holes.

        Parameters
        ----------
        bbox : tuple
            left, right, bottom, top
        hole_type : str
        start : str
            Date string. Recommended format is yyyy-mm-dd.
            Value is passed to `pandas.to_datetime`.
        end : str
            Date string. Recommended format is yyyy-mm-dd.
            Value is passed to `pandas.to_datetime`.
        fmt : str
            Custom date string format for `start` and `end`.
            Value is passed for `datetime.strptime`.
            See https://docs.python.org/3.7/library/datetime.html#strftime-and-strptime-behavior

        Returns
        -------
        list
            Filtered holes.

        Examples
        --------
        filtered_holes = holes_object.filter_holes(
             bbox=(24,25,60,61)
        )

        filtered_holes = holes_object.filter_holes(
            hole_type=["PO"]
        )

        filtered_holes = holes_object.filter_holes(
            start="2015-05-15", end="2016-08-06"
        )

        filtered_holes = holes_object.filter_holes(
            start="05/15/15", end="08/06/16", fmt="%x"
        )

        Return types are from:
            _filter_coordinates(bbox, **kwargs)
            _filter_type(hole_type, **kwargs)
            _filter_date(start=None, end=None, fmt=None, **kwargs)
        """
        filtered_holes = self.holes
        if bbox is not None:
            filtered_holes = self._filter_coordinates(filtered_holes, bbox, **kwargs)
        if hole_type is not None:
            filtered_holes = self._filter_type(filtered_holes, hole_type, **kwargs)
        if start is not None or end is not None:
            filtered_holes = self._filter_date(filtered_holes, start, end, fmt=fmt, **kwargs)
        return filtered_holes

    def _filter_coordinates(self, holes, bbox):
        """Filter object by coordinates."""
        xmin, xmax, ymin, ymax = bbox
        filtered_holes = []
        for hole in holes:
            if not (
                hasattr(hole.header, "XY")
                and "X" in hole.header.XY.keys()
                and "Y" in hole.header.XY.keys()
            ):
                continue
            if (
                hole.header.XY["X"] >= xmin
                and hole.header.XY["X"] <= xmax
                and hole.header.XY["Y"] >= ymin
                and hole.header.XY["Y"] <= ymax
            ):
                filtered_holes.append(hole)
        return Holes(filtered_holes)

    def _filter_type(self, holes, hole_type):
        """Filter object by survey abbreviation (type)."""
        filtered_holes = []
        if isinstance(hole_type, str):
            hole_type = [hole_type]
        for hole in holes:
            if (
                hasattr(hole.header, "TT")
                and ("Survey abbreviation" in hole.header.TT)
                and any(item == hole.header.TT["Survey abbreviation"] for item in hole_type)
            ):
                filtered_holes.append(hole)
        return Holes(filtered_holes)

    def _filter_date(self, holes, start=None, end=None, fmt=None):
        """Filter object by datetime."""
        if isinstance(start, str) and fmt is None:
            start = pd.to_datetime(start)
        elif isinstance(start, str) and fmt is not None:
            start = datetime.strptime(start, fmt)

        if isinstance(end, str) and fmt is None:
            end = pd.to_datetime(end)
        elif isinstance(end, str) and fmt is not None:
            end = datetime.strptime(end, fmt)

        filtered_holes = []
        for hole in holes:
            date = hole.header.date
            if pd.isnull(date):
                continue
            if isinstance(date, str):
                continue
            sbool = (date >= start) if start is not None else True
            ebool = (date <= end) if end is not None else True
            if sbool and ebool:
                filtered_holes.append(hole)
        return Holes(filtered_holes)

    def value_counts(self):
        """Count for each subgroup."""
        counts = {}
        for hole in self.holes:
            if hasattr(hole.header, "TT") and ("Survey abbreviation" in hole.header.TT):
                value = hole.header.TT["Survey abbreviation"]
                if value not in counts:
                    counts[value] = 0
                counts[value] += 1
            else:
                if "Missing survey abbreviation" not in counts:
                    counts["Missing survey abbreviation"] = 0
                counts["Missing survey abbreviation"] += 1
        return counts

    def drop_duplicates(self):
        """Check if hole headers/datas are unique; drop duplicates."""
        raise NotImplementedError

    def to_csv(self, path, **kwargs):
        """Save data in table format to CSV.

        Paramaters
        ----------
        path : str
        kwargs
            Passed to `pandas.DataFrame.to_csv` function.
        """
        _, ext = os.path.splitext(path)
        if ext not in (".txt", ".csv"):
            msg = "Found extension {}, use '.csv' or '.txt'.".format(path)
            logger.critical(msg)
            raise FileExtensionMissingError(msg)
        with open(path, "w") as f:
            self.get_dataframe().to_csv(f, **kwargs)

    def to_excel(self, path, **kwargs):
        """Save data in table format to Excel.

        Paramaters
        ----------
        path : str
        kwargs
            Passed to `pandas.DataFrame.to_csv` function.
        """
        _, ext = os.path.splitext(path)
        if ext not in (".xlsx", ".xls"):
            msg = "ext not in ('.xlsx', '.xls'): {}".format(path)
            logger.critical(msg)
            raise FileExtensionMissingError(msg)
        with pd.ExcelWriter(path) as writer:  # pylint: disable=abstract-class-instantiated
            self.get_dataframe().to_excel(writer, **kwargs)

    def to_infraformat(self, path, split=False, namelist=None):
        """Save data in infraformat.

        Parameters
        ----------
        path : str
            path to save data
        split : bool, optional
            save in invidual files
        namelist : list, optional
            filenames for each file
            valid only if split is True
        """
        from .io import to_infraformat  # pylint: disable=cyclic-import

        if split:
            use_format = False
            if namelist is None:
                if not "{}" in path:
                    msg = "Use either a {} or a namelist for filenames"
                    logger.critical(msg)
                    raise ValueError(msg)
                use_format = True
            else:
                assert len(namelist) == len(self.holes)
            for i, hole in self.holes:
                if use_format:
                    path_ = path.format(i)
                else:
                    path_ = namelist[i]
                to_infraformat([hole], path_)
        else:
            to_infraformat(self.holes, path)

    def plot_map(self, render_holes=True, progress_bar=True, popup_size=(3, 3)):
        """Plot a leaflet map from holes with popup hole plots.

        Parameters
        ----------
        holes : holes object
        render_holes : bool
            Render popup diagrams for holes
        progress_bar : bool
            Show tqdm progress bar while adding/rendering holes
        popup_size : tuple
            size in inches of popup figure

        Returns
        -------
        map_fig : folium map object
        """
        from ..plots.maps import plot_map as _plot_map

        return _plot_map(self, render_holes, progress_bar, popup_size)

    def project(self, output="EPSG:4326", check="Finland", output_height=False):
        """Transform holes -objects coordinates.

        Creates deepcopy of holes and drops invalid holes. Warns into logger.

        Parameters
        ----------
        output : str
            ESPG code, 'EPSG:XXXX' or name of the coordinate system. Check
            pyinfraformat.coord_utils.EPSG_SYSTEMS for possible values.
        check : str
            Check if points are inside area. Raises warning into logger.
            Possible values: 'Finland', 'Estonia', False
        output_height : str
            output height system. Possible values N43, N60, N2000 and False.
            False for no height system change or checks.

        Returns
        -------
        holes : Holes -object
            Copy of holes with coordinates and height transformed

        Examples
        --------
        holes_gk25 = holes.project(output="GK25", check="Finland", output_height="N2000")
        """
        from ..core.coord_utils import project_holes

        return project_holes(self, output, check, output_height)

    def get_endings(self, check_height=True):
        """Get dataframe with every holes last data row with soil observation."""
        if check_height:
            if len({hole.fileheader.KJ["Height reference"] for hole in self}) != 1:
                raise ValueError("Holes must have uniform height reference.")
            if any((hole.fileheader.KJ["Height reference"] in {"?", "Unknown"} for hole in self)):
                raise ValueError("Unknown height reference system.")
        soil_observations = []
        for hole in self:
            if not (
                hasattr(hole, "header")
                and hasattr(hole.header, "XY")
                and ("X" in hole.header.XY)
                and ("Y" in hole.header.XY)
                and "Z-start" in hole.header.XY
            ):
                continue
            if not (
                hasattr(hole, "survey")
                and hasattr(hole.survey, "data")
                and len(hole.survey.data) > 0
            ):
                continue
            point_x = hole.header.XY["X"]
            point_y = hole.header.XY["Y"]
            z_start = hole.header.XY["Z-start"]
            abbrev = hole.header.TT["Survey abbreviation"].upper()
            ending = hole.header["-1"]["Ending"].upper()
            if abbrev == "PO" and ending == "KA":
                df = hole.get_dataframe()
                if "data_Soil type" in df.columns:
                    if df["data_Soil type"].str.upper().iloc[0] == "KA":
                        if df["data_Depth (m)"].iloc[0] > 0.5:
                            soil_depth = df["data_Depth (m)"].iloc[0]
                        else:
                            soil_depth = 0.0
                    elif sum(df["data_Soil type"].str.upper() == "KA") == 0:
                        logger.warning(
                            "Hole ending 'KA' without any 'KA' soil observations, omitting."
                        )
                    else:
                        slicer = df["data_Soil type"].str.upper() == "KA"
                        slicer = slicer.shift(-1, fill_value=False)
                        soil_depth = df[slicer]["data_Depth (m)"].iloc[-1]
                    soil_observations.append(
                        (point_x, point_y, z_start, z_start - soil_depth, abbrev, ending)
                    )
            elif abbrev in ["NO", "NE"]:
                if "Depth info 1 (m)" not in hole.survey.data[-1]:
                    continue
                soil_depth = max(
                    [
                        hole.survey.data[-1]["Depth info 1 (m)"],
                        hole.survey.data[-1]["Depth info 2 (m)"],
                    ]
                )
                soil_observations.append(
                    (point_x, point_y, z_start, z_start - soil_depth, abbrev, ending)
                )

            elif abbrev in ["KE", "KR"]:
                # Bedrock analysis drillings
                pass
            else:
                if "Depth (m)" not in hole.survey.data[-1]:
                    continue
                soil_depth = hole.survey.data[-1]["Depth (m)"]
                soil_observations.append(
                    (point_x, point_y, z_start, z_start - soil_depth, abbrev, ending)
                )
        columns = ["X", "Y", "Z-start", "Last_soil", "Abbreviation", "Ending"]
        return pd.DataFrame.from_records(soil_observations, columns=columns)

    def get_list(self):
        """Get survey data, hole header and fileheader as list of dicts."""
        return_list = []
        for hole in self:
            d_header = hole.get_header_dict()
            dict_list = hole.get_data_list()
            d_fileheader = hole.get_fileheader_dict()
            return_list.append({"header": d_header, "fileheader": d_fileheader, "data": dict_list})
        return return_list

    def get_columns(self):
        """Get survey data, header and fileheader columns."""
        return_set = set()
        for hole in self:
            return_set = return_set.union(hole.get_columns())
        return return_set

    def get_dataframe(self, skip_columns=False):
        """Get survey data, hole header and fileheader as DataFrame.

        Paramaters
        ----------
        skip_columns : list, str or False
            Columns that will be excluded. Not case sensitive.
            Uses wildcards (* and ?) to match strings (see fnmatch).
            See get_columns() for columns included.

        Examples
        --------
        >>> holes.get_dataframe(skip_columns="*laboratory*")
        >>> holes.get_dataframe(skip_columns=["*lab*", "*sieve*", "*header*"])
        """
        df_list = [hole.get_dataframe(skip_columns) for hole in self.holes]
        return pd.concat(df_list, axis=0, sort=False)


class Hole:
    """Class to hold Hole information."""

    def __init__(self):
        self.fileheader = FileHeader()
        self.header = Header()
        self.inline_comment = InlineComment()
        self.survey = Survey()
        self._illegal = Illegal()

    def __str__(self):

        msg = str(self.header).replace("\n", "\n  ")
        return "Infraformat Hole -object:\n  {}".format(msg)

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        if isinstance(other, Holes):
            return Holes([self] + other.holes)
        if isinstance(other, Hole):
            return Holes([self] + [other])
        raise ValueError("Only Holes or Hole -objects can be added.")

    def add_fileheader(self, key, fileheader):
        """Add fileheader to object."""
        self.fileheader.add(key, fileheader)

    def add_header(self, key, header):
        """Add header to object."""
        self.header.add(key, header)

    def add_inline(self, key, inline):
        """Add inline object to object."""
        self.inline_comment.add(key, inline)

    def add_survey(self, survey):
        """Add survey information to object."""
        self.survey.add(survey)

    def _add_illegal(self, illegal):
        """Add illegal lines to object."""
        self._illegal.add(illegal)

    def plot(self, output="figure", figsize=(4, 4)):
        """Plot a diagram of a sounding with matplotlib.

        Parameters
        ----------
        output : str
            Possible values: ['figure', 'svg']
        figsize : tuple
            figure size in inches

        Returns
        -------
        figure : matplotlib figure or svg
        """
        from ..plots.holes import plot_hole

        return plot_hole(self, output, figsize)

    def get_header_dict(self):
        """Get hole header as a dict."""
        d_header = {}
        for key in self.header.keys:
            for key_, item in getattr(self.header, key).items():
                d_header["{}_{}".format(key, key_)] = item
        return d_header

    def get_data_list(self):
        """Get survey data as a list of dict."""
        dict_list = self.survey.data
        return dict_list

    def get_fileheader_dict(self):
        """Get fileheader as a dict."""
        d_fileheader = {}
        for key in self.fileheader.keys:
            for key_, item in getattr(self.fileheader, key).items():
                d_fileheader["{}_{}".format(key, key_)] = item
        return d_fileheader

    def get_dict(self):
        """Get survey data, hole header and fileheader as dict."""
        d_header = self.get_header_dict()
        dict_list = self.get_data_list()
        d_fileheader = self.get_fileheader_dict()
        return {"header": d_header, "fileheader": d_fileheader, "data": dict_list}

    def get_columns(self):
        """Get survey data, header and fileheader columns."""
        data = set("data_" + item for row in self.survey.data for item in row)
        fileheader = {
            f"fileheader_{key}_{item}"
            for key in self.fileheader.keys
            for item in getattr(self.fileheader, key).keys()
        }
        header = {
            f"header_{key}_{item}"
            for key in self.header.keys
            for item in getattr(self.header, key).keys()
        }
        return data.union(fileheader).union(header)

    def get_dataframe(self, skip_columns=False):
        """Get survey data, hole header and fileheader as DataFrame.

        Paramaters
        ----------
        skip_columns : list, str or False
            Columns that will be excluded. Not case sensitive.
            Uses wildcards (* and ?) to match strings (see fnmatch).
            See get_columns() for columns included.

        Examples
        --------
        >>> hole.get_dataframe(skip_columns="*laboratory*")
        >>> hole.get_dataframe(skip_columns=["*lab*", "*sieve*", "*header*"])
        """
        if skip_columns:
            skip_columns = (
                [
                    skip_columns,
                ]
                if isinstance(skip_columns, str)
                else skip_columns
            )
        dict_list = self.get_data_list()
        dict_list = [{"data_" + item: row[item] for item in row} for row in dict_list]
        if skip_columns:
            skip_data = []
            for row in skip_columns:
                for data in dict_list:
                    keys = data.keys()
                    for key in keys:
                        skip_data.extend(fnmatch.filter(data, row))
            dict_list = [
                {item: row[item] for item in row if item not in skip_data} for row in dict_list
            ]
        dict_list = [item for item in dict_list if len(item) > 0]
        df = pd.DataFrame(dict_list if len(dict_list) > 0 else [{"dummy": 0}])

        d_header = self.get_header_dict()
        d_header = {"header_" + key: item for key, item in d_header.items()}
        for key in d_header:
            if skip_columns and any((fnmatch.fnmatch(key, item) for item in skip_columns)):
                continue
            df[key] = d_header[key]

        d_fileheader = self.get_fileheader_dict()
        d_fileheader = {"fileheader_" + key: d_header[key] for key in d_header}
        for key in d_fileheader:
            if skip_columns and any((fnmatch.fnmatch(key, item) for item in skip_columns)):
                continue
            df[key] = d_fileheader[key]

        return df if len(dict_list) > 0 else df.drop("dummy", axis=1)


class FileHeader:
    """Class to hold file header information."""

    def __init__(self):
        self.keys = set()

    def add(self, key, values):
        """Add member to class."""
        setattr(self, key, values)
        self.keys.add(key)

    def __str__(self):
        msg = "FileHeader object - Fileheader contains {} items\n  {}".format(
            len(self.keys), pprint.pformat(self.__dict__)
        )
        return msg

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, attr):
        if attr in self.keys:
            return getattr(self, attr)
        else:
            raise TypeError("Attribute not found: {}".format(attr))


class Header:
    """Class to hold header information."""

    def __init__(self):
        self.keys = set()
        self.date = pd.NaT

    def add(self, key, values):
        """Add header items to object."""
        if key == "XY" and ("Date" in values):
            try:
                if len(values["Date"]) == 6:
                    date = datetime.strptime(values["Date"], "%d%m%y")
                elif len(values["Date"]) == 8:
                    date = datetime.strptime(values["Date"], "%d%m%Y")
                else:
                    date = pd.to_datetime(values["Date"])
            except ValueError:
                date = pd.NaT
            if date.year < 1900:
                date = pd.NaT
            self.date = date
        setattr(self, key, values)
        self.keys.add(key)

    def __str__(self):

        msg = pprint.pformat(self.__dict__)
        return "Hole Header -object:\n  {}".format(msg)

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, attr):
        if attr in self.keys:
            return getattr(self, attr)
        else:
            raise TypeError("Attribute not found: {}".format(attr))


class InlineComment:
    """Class to inline comments."""

    def __init__(self):
        self.data = list()

    def add(self, key, values):
        """Add inline comments to object."""
        self.data.append((key, values))

    def __str__(self):

        msg = pprint.pformat(self.__dict__)
        return "Hole InlineComment -object:\n  {}".format(msg)

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, attr):
        return self.data[attr]


class Survey:
    """Class to survey information."""

    def __init__(self):
        self.data = list()

    def add(self, values):
        """Add survey information to object."""
        self.data.append(values)

    def __str__(self):

        msg = pprint.pformat(self.__dict__)
        return "Hole Survey -object:\n  {}".format(msg)

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, attr):
        return self.data[attr]


class Illegal:
    """Class to contain illegal lines."""

    def __init__(self):
        self.data = list()

    def add(self, values):
        """Add illegal lines to object."""
        self.data.append(values)

    def __str__(self):

        msg = pprint.pformat(self.__dict__)
        return "Hole Illegal -object:\n  {}".format(msg)

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, attr):
        return self.data[attr]
