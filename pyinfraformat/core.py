from gc import collect
import logging

from .parser import identifiers
from .io import from_infraformat, to_infraformat

logger = logging.getLogger("pyinfraformat")

__all__ = ["Holes"]


class FileExtensionMissing(Exception):
    def __init__(self):
        self.msg = "File extension is missing"

    def __str__(self):
        return repr(self.msg)


class Holes:
    """
    Container for multiple infraformat hole information.
    """

    def __init__(self, holes, lowmemory=False):
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
        msg = f"Infraformat Holes object:\n  Total of {len(self.holes)} holes"
        counts = "\n".join(
            f"    -{key}: {value}" for key, value in dict(self.value_counts()).items()
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

    def filter_holes(by="coordinates", **kwargs):
        """filter_coordinates(bbox)
        filter_surveys(survey_abbreviation)
        filter_date(start=None, end=None)

        bbox : left, right, bottom, top

        Parameters
        ----------
        by : str {'coordinate', 'survey', 'date'}
        """
        if by == "coordinates":
            self._filter_coordinates(**kwargs)
        elif by == "survey":
            self._filter_surveys(**kwargs)
        elif by == "date":
            self._filter_date(**kwargs)

    def _filter_coordinates(self, bbox):
        """Filter object by coordinates"""
        xmin, xmax, ymin, ymax = bbox
        xrange = range(xmin, xmax)
        yrange = range(ymin, ymax)
        holes = []
        for hole in self.holes:
            if not (("X" in hole.header) and ("Y" in hole.header)):
                continue
            if hole.header.XY["X"] in xrange and hole.header.XY["Y"] in yrange:
                holes.append(hole)
        return Holes(holes)

    def _filter_surveys(self, survey_abbreviation):
        """Slice object by survey abbreviation"""
        holes = []
        for hole in self.holes:
            if (
                ("TT" in hole.header)
                and ("Survey abbreviation" in hole.header.TT)
                and (hole.header.TT["Survey abbreviation"] == survey_abbreviation)
            ):
                holes.append(hole)
        return Holes(holes)

    def _filter_date(self, start=None, end=None):
        """Filter object by datetime"""

        if start is None and end is None:
            return Holes(self.holes)

        holes = []
        for hole in self.holes:
            if ("XY" in hole.header) and ("Date" in hole.header["XY"]):
                date = hole.header["XY"]["Date"]
                sbool = (date >= start) if start is not None else True
                ebool = (date <= end) if end is not None else True
                if sbool and ebool:
                    holes.append(hole)
        return Holes(holes)

    def value_counts(self):
        counts = {}
        for hole in self.holes:
            if ("TT" in hole.header) and ("Survey abbreviation" in hole.header["TT"]):
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
                tmp_df = concat((tmp_df, hole_df), axis=0, sort=False)
                del hole._dataframe, hole_df
                collect()
            self._dataframe = tmp_df
        else:
            df_list = [hole._get_dataframe(update=True) for hole in self.holes]
            self._dataframe = concat(df_list, axis=0, sort=False)
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
            raise FileExtensionMissingError(": {}, use '.csv' or '.txt'".format(path))
        with open(path, "r") as f:
            self.dataframe.to_csv(f, **kwargs)

    def to_excel(self, path, **kwargs):
        _, ext = os.path.splitext(path)
        if ext not in (".xlsx", ".xls"):
            raise FileExtensionMissingError(": {}".format(path))
        with ExcelWriter(path) as writer:
            self.dataframe.to_excel(writer, **kwargs)

    def to_infraformat(self, path, split=False, namelist=None):
        """
        Parameters
        ----------
        path : str
            path to save data
        split : bool
            save files in invidual files
        namelist : list
            filenames for each file
            valid only if split is True
        """
        if split:
            use_format = False
            if namelist is None:
                if not "{}" in path:
                    raise ValueError("Use either a \{\} or a namelist for filenames")
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
