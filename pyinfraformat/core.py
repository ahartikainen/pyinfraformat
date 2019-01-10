"""Core function for PyInfraformat"""
import pandas as pd
from datetime import datetime
from gc import collect
import logging
import os

from .parser import identifiers
from .io import from_infraformat, to_infraformat

logger = logging.getLogger("pyinfraformat")

__all__ = ["Holes"]


class Holes:
    """
    Container for multiple infraformat hole information.
    """

    def __init__(self, holes=None, lowmemory=False):
        """Container for multiple infraformat hole information.

        Parameters
        ----------
        holes : list
            list of infraformat hole information
        lowmemory : bool, optional
        """
        if holes is None:
            holes = []
        self.holes = holes
        self._lowmemory = lowmemory

    def add_holes(self, holes):
        """Add list of holes to class"""
        self.holes.extend(holes)

    def __str__(self):
        msg = f"Infraformat Holes -object:\n  Total of {len(self.holes)} holes"
        value_counts = self.value_counts()
        if self.holes:
            max_length = max([len(str(values)) for values in value_counts.values()]) + 1
            counts = "\n".join(
                "    - {key} ...{value:.>7}".format(
                    key=key, value=("{:>" + f"{max_length}" + "}").format(value)
                )
                for key, value in value_counts.items()
            )
            msg = "\n".join((msg, counts))
        return msg

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, index):
        return self.holes[index]

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
        return Holes(self.holes + other.holes)

    def filter_holes(
        self,
        by="coordinates",
        *,
        bbox=None,
        hole_type=None,
        start=None,
        end=None,
        fmt=None,
        **kwargs,
    ):
        """Filter holes.

        Parameters
        ----------
        by : str {'coordinate', 'survey', 'date'}
        bbox : tuple
            left, right, bottom, top
        hole_type : str
        start : str
            Date string. Format is either yyyy-mm-dd or `fmt`.
        end : str
            Date string. Format is either yyyy-mm-dd or `fmt`.
        fmt : str
            Date string format.

        Returns
        -------
        list
            List containing filtered holes.

        Examples
        --------

        Return types are:
            _filter_coordinates(bbox, **kwargs)
            _filter_type(hole_type, **kwargs)
            _filter_date(start=None, end=None, fmt=None, **kwargs)
        """
        if by == "coordinates":
            filtered_holes = self._filter_coordinates(bbox)
        elif by == "type":
            filtered_holes = self._filter_type(type)
        elif by == "date":
            filtered_holes = self._filter_date(start, end)
        else:
            raise TypeError("Argument was not valid: by={by}")
        return filtered_holes

    def _filter_coordinates(self, bbox):
        """Filter object by coordinates"""
        if bbox is None:
            return Holes(self.holes)
        xmin, xmax, ymin, ymax = bbox
        xrange = range(xmin, xmax)
        yrange = range(ymin, ymax)
        holes = []
        for hole in self.holes:
            if not (hasattr(hole.header, "X") and hasattr(hole.header, "Y")):
                continue
            if hole.header.XY["X"] in xrange and hole.header.XY["Y"] in yrange:
                holes.append(hole)
        return Holes(holes)

    def _filter_type(self, type):
        """Filter object by survey abbreviation (type)"""
        if type is None:
            Holes(self.holes)
        holes = []
        if isinstance(type, str):
            type = [type]
        for hole in self.holes:
            if (
                hasattr(hole.header, "TT")
                and ("Survey abbreviation" in hole.header.TT)
                and any(item == hole.header.TT["Survey abbreviation"] for item in type)
            ):
                holes.append(hole)
        return Holes(holes)

    def _filter_date(self, start=None, end=None, fmt=None):
        """Filter object by datetime"""

        if start is None and end is None:
            return Holes(self.holes)

        if isinstance(start, str) and fmt is None:
            start = pd.to_datetime(start)
        elif isinstance(start, str) and fmt is not None:
            start = datetime.strptime(start, fmt)

        if isinstance(end, str) and fmt is None:
            end = pd.to_datetime(end)
        elif isinstance(end, str) and fmt is not None:
            end = datetime.strptime(end, fmt)

        holes = []
        for hole in self.holes:
            date = hole.header.date
            if pd.isnull(date):
                continue
            if isinstance(date, str):
                continue
            sbool = (date >= start) if start is not None else True
            ebool = (date <= end) if end is not None else True
            if sbool and ebool:
                holes.append(hole)
        return Holes(holes)

    def value_counts(self):
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
        """TODO:
        Check if hole headers/datas are unique; drop duplicates"""
        raise NotImplementedError

    @property
    def dataframe(self):
        """Create pandas.DataFrame
        """
        return self._get_dataframe()

    def _get_dataframe(self):
        if not self.holes:
            return pd.DataFrame()
        elif self._lowmemory:
            tmp_df = DataFrame()
            for hole in self.holes:
                hole_df = hole._get_dataframe(update=True).copy()
                tmp_df = pd.concat((tmp_df, hole_df), axis=0, sort=False)
                del hole._dataframe, hole_df
                collect()
            self._dataframe = tmp_df
        else:
            df_list = [hole._get_dataframe(update=True) for hole in self.holes]
            self._dataframe = pd.concat(df_list, axis=0, sort=False)
        return self._dataframe

    def to_csv(self, path, **kwargs):
        """
        Paramaters
        ----------
        path : str
            path to save data
        kwargs
            keyword arguments going for pandas.DataFrame.to_csv function
        """
        _, ext = os.path.splitext(path)
        if ext not in (".txt", ".csv"):
            msg = ": {}, use '.csv' or '.txt'".format(path)
            logger.critical(msg)
            raise FileExtensionMissing()
        with open(path, "w") as f:
            self.dataframe.to_csv(f, **kwargs)

    def to_excel(self, path, **kwargs):
        _, ext = os.path.splitext(path)
        if ext not in (".xlsx", ".xls"):
            msg = "ext not in ('.xlsx', '.xls'): {}".format(path)
            logger.critical(msg)
            raise FileExtensionMissing()
        with ExcelWriter(path) as writer:
            self.dataframe.to_excel(writer, **kwargs)

    def to_infraformat(self, path, split=False, namelist=None):
        """
        Parameters
        ----------
        path : str
            path to save data
        split : bool
            save in invidual files
        namelist : list
            filenames for each file
            valid only if split is True
        """
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
                pass
                if use_format:
                    path_ = path.format(i)
                else:
                    path_ = namelist[i]
                to_infraformat([hole], path_)
        else:
            to_infraformat(self.holes, path)
