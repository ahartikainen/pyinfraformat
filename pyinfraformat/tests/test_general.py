import pyinfraformat as pif
import pytest


@pytest.mark.parametrize("language", ["fi", "Fi", "FI", "fI"])
def test_info(language):
    assert pif.print_info() is None
    assert pif.print_info(language=language) is None
    assert isinstance(pif._info_fi(), str)


@pytest.mark.parametrize("language", ["se", "en", "fin"])
def test_info_bad(language):
    with pytest.raises(NotImplementedError):
        pif.print_info(language)
