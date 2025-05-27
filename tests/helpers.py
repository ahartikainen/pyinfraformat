"""Helper functions for tests."""

from pyinfraformat import Holes, from_gtk_wfs
from requests.exceptions import HTTPError


def ping_gtk():
    try:
        bbox = (60.2, 24.8, 60.215, 24.83)
        holes = from_gtk_wfs(bbox, "EPSG:4326")
        result = not Holes(holes[:3]).get_dataframe().empty
    except HTTPError:
        return True
