import pyinfraformat as pif
import pytest


def test_info():
    assert print_info() is None
    assert isinstance(_info_fi(), str) 


def test_info_bad()
    with pytest.raises(NotImplementedError):
        print_info(language="se")
    with pytest.raises(NotImplementedError):
        print_info(language="en")
