from .parser import read as _read, identifiers
from .io import to_infraformat

from pandas import DataFrame, concat, ExcelWriter
from gc import collect


class HolesNotFound(Exception):
    def __init__(self):
        self.msg = "No holes added to class"

    def __str__(self):
        return repr(self.msg)


class FileExtensionMissing(Exception):
    def __init__(self):
        self.msg = "File extension is missing"

    def __str__(self):
        return repr(self.msg)


class Infraformat:
    """
    Python Class to process infraformat files

    Paramaters
    ----------
    path : str, optional, default None
        path to read data (file / folder / glob statement, see use_glob)
    verbose : bool, optional, default True
    lowmemory : bool, optional, default False
        parameter for pandas.DataFrame creation
    encoding : str, optional, default 'utf-8'
        file encoding, if 'utf-8' fails, code will try to use 'latin-1'
    use_glob : bool, optional, default False
        path is a glob string
    extension : bool, optional, default None
    robust_read : bool, optional, default False
        Enable reading ill-defined holes
    """

    def __init__(self, path=None, verbose=False, **kwargs):
        """
        Paramaters
        ----------
        path : str, optional, default None
            path to read data (file / folder / glob statement, see use_glob)
        verbose : bool, optional, default True
        lowmemory : bool, optional, default False
            parameter for pandas.DataFrame creation
        encoding : str, optional, default 'utf-8'
            file encoding, if 'utf-8' fails, code will try to use 'latin-1'
        use_glob : bool, optional, default False
            path is a glob string
        extension : bool, optional, default None
        robust_read : bool, optional, default False
            Enable reading ill-defined holes
        """
        self._verbose = verbose
        self._lowmemory = kwargs.get("lowmemory", False)

        if path is not None:
            self.read(
                path=path,
                encoding=kwargs.get("encoding", "utf-8"),
                use_glob=kwargs.get("use_glob", False),
                extension=kwargs.get("extension", None),
                robust_read=kwargs.get("robust_read", False),
            )

    def read(self, path, encoding="utf-8", use_glob=False, extension=None, robust_read=False):
        """
        Paramaters
        ----------
        path : str, optional, default None
            path to read data (file / folder / glob statement, see use_glob)
        encoding : str, optional, default 'utf-8'
            file encoding, if 'utf-8' fails, code will try to use 'latin-1'
        use_glob : bool, optional, default False
            path is a glob string
        extension : bool, optional, default None
        robust_read : bool, optional, default False
            Enable reading ill-defined holes
        """
        holes = _read(
            path, encoding=encoding, use_glob=use_glob, extension=extension, robust_read=robust_read
        )
        if hasattr(self, "holes"):
            self.holes.extend(holes)
        else:
            self.holes = holes

    @property
    def dataframe(self):
        """Create pandas.DataFrame
        """
        return self._get_dataframe(update=None)

    def _get_dataframe(self, update=None):
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
        if hasattr(self, "holes"):

            if hasattr(self, "_dataframe") and update == False:
                pass
                # return ._dataframe end of this if
            elif hasattr(self, "_dataframe") and update is None:
                new_dfs = [hole.dataframe for hole in self.holes if not hasattr(hole, "_dataframe")]
                if new_dfs:
                    df_list = [self._dataframe]
                    df_list.extend(new_dfs)
                    self._dataframe = concat(df_list)
            else:
                # TODO: Make this smarter
                if self._lowmemory:
                    tmp_df = DataFrame()
                    for hole in self.holes:
                        hole_df = hole._get_dataframe(update=True).copy()
                        tmp_df = concat((tmp_df, hole_df), axis=0)
                        del hole._dataframe, hole_df
                        collect()
                    self._dataframe = tmp_df
                else:
                    df_list = [hole._get_dataframe(update=True) for hole in self.holes]
                    self._dataframe = concat(df_list)
            return self._dataframe
        else:
            raise HolesNotFoundError()

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
