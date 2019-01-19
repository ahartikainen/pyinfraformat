import pyinfraformat as pif
import pytest


test.mark.parametrize("language", ['fi', 'Fi', 'FI', 'fI'])
def test_info(language):
    assert print_info() is None
    assert print_info(language=language) is None
    assert isinstance(_info_fi(), str) 


@pytest.mark.parametrize("language", ['se', 'en', 'fin'])
def test_info_bad(language):
    with pytest.raises(NotImplementedError):
        print_info(language)
