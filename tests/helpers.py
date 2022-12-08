"""Helper functions for tests."""
from pyinfraformat import Holes, from_gtk_wfs


def ping_gtk():
    bbox = (60.2, 24.8, 60.215, 24.83)
    holes = from_gtk_wfs(bbox, "EPSG:4326")
    return not Holes(holes[:3]).get_dataframe().empty
