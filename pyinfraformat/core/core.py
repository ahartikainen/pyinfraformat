"""Core function for pyinfraformat."""
import logging
import os
from datetime import datetime
from gc import collect
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
            max_length = max([len(str(values)) for values in value_counts.values()]) + 1
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

    @property
    def dataframe(self):
        """Create pandas.DataFrame."""
        return self._get_dataframe()

    # pylint: disable=protected-access, attribute-defined-outside-init
    def _get_dataframe(self):
        """Build and combine DataFrame."""
        if not self.holes:
            return pd.DataFrame()
        elif self._lowmemory:
            tmp_df = pd.DataFrame()
            for hole in self.holes:
                hole_df = hole._get_dataframe(update=True).copy()
                tmp_df = pd.concat((tmp_df, hole_df), axis=0, sort=False)
                del hole._dataframe, hole_df
                collect()
            self._dataframe = tmp_df
        else:
            df_list = [hole._get_dataframe(update=True) for hole in self.holes]
            self._dataframe = pd.concat(df_list, axis=0, sort=False)
        collect()
        return self._dataframe

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
            self.dataframe.to_csv(f, **kwargs)

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
            self.dataframe.to_excel(writer, **kwargs)

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

    def plot_map(self, render_holes=True):
        """Plot a leaflet map from holes with popup hole plots.

        Parameters
        ----------
        render_holes : bool
            Render popup diagrams for holes

        Returns
        -------
        map_fig : folium map object
        """
        from ..plots.maps import plot_map as _plot_map

        return _plot_map(self, render_holes)

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
            if not self._dataframe.empty:  # pylint: disable=access-member-before-definition
                return self._dataframe  # pylint: disable=access-member-before-definition

        dict_list = self.survey.data
        if not dict_list:
            msg = "No data in Hole object. Header: {}".format(self.__str__())
            logger.warning(msg)
            return pd.DataFrame()
        self._dataframe = pd.DataFrame(dict_list)  # pylint: disable=attribute-defined-outside-init
        self._dataframe.columns = ["data_{}".format(col) for col in self._dataframe.columns]
        for key in self.header.keys:
            self._dataframe.loc[:, "Date"] = self.header.date
            for key_, item in getattr(self.header, key).items():
                self._dataframe.loc[:, "header_{}_{}".format(key, key_)] = item
        for key in self.fileheader.keys:
            for key_, item in getattr(self.fileheader, key).items():
                self._dataframe.loc[:, "fileheader_{}_{}".format(key, key_)] = item

        return self._dataframe

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


class FileHeader:
    """Class to hold file header information."""

    def __init__(self):
        self.keys = set()

    def add(self, key, values):
        """Add member to class."""
        setattr(self, key, values)
        self.keys.add(key)

    def __str__(self):
        msg = "FileHeader object - Fileheader contains {} items".format(len(self.keys))
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

    def __getitem__(self, attr):
        return self.data[attr]


class Survey:
    """Class to survey information."""

    def __init__(self):
        self.data = list()

    def add(self, values):
        """Add survey information to object."""
        self.data.append(values)

    def __getitem__(self, attr):
        return self.data[attr]


class Illegal:
    """Class to contain illegal lines."""

    def __init__(self):
        self.data = list()

    def add(self, values):
        """Add illegal lines to object."""
        self.data.append(values)

    def __getitem__(self, attr):
        return self.data[attr]
