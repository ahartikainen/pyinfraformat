import numpy as np
import pytest

from pyinfraformat.utils import print_info, info_fi, custom_int, custom_float


@pytest.mark.parametrize("language", ["fi", "Fi", "FI", "fI"])
def test_info(language):
    assert print_info() is None
    assert print_info(language=language) is None
    assert isinstance(info_fi(), str)


@pytest.mark.parametrize("language", ["se", "en", "fin"])
def test_info_bad(language):
    with pytest.raises(NotImplementedError):
        print_info(language)


@pytest.mark.parametrize("nums", [("1", 1), ("1_000", 1000), ("0", 0)])
def test_custom_int_pure(nums):
    """Input string num and number pair"""
    str_num, num = nums
    custom_integer = custom_int(str_num)
    assert custom_integer == num
    assert isinstance(custom_integer, int)


@pytest.mark.parametrize("nums", [("1.", 1), ("1_000,0", 1000), (".0", 0), ("1,0e3", 1000)])
def test_custom_int_pure(nums):
    """Input string num and number pair"""
    str_num, num = nums
    custom_integer = custom_int(str_num)
    assert custom_integer == num
    assert isinstance(custom_integer, int)


@pytest.mark.parametrize(
    "nums", [(".1", 0.1), ("1.1", 1.1), ("1_000,1", 1000.1), ("1,2345e3", 1234.5)]
)
def test_custom_int_to_float(nums):
    str_num, num = nums
    custom_integer = custom_int(str_num)
    assert custom_integer == num
    assert isinstance(custom_integer, float)
    assert not np.isnan(custom_integer)


@pytest.mark.parametrize("num", ["-", "nan", "NaN", "NA", "test", "value", "1.2a"])
def test_custom_int_nan(num):
    custom_integer = custom_int(num)
    assert isinstance(custom_integer, float)
    assert np.isnan(custom_integer)


@pytest.mark.parametrize("nums", [("1", 1.0), ("1_000,2", 1000.2), ("1e3", 1e3)])
def test_custom_float(nums):
    str_num, num = nums
    custom_floating = custom_float(str_num)
    assert custom_floating == num
    assert isinstance(custom_floating, float)
    assert not np.isnan(custom_floating)


@pytest.mark.parametrize("num", ["-", "nan", "NaN", "NA", "test", "string", "1.2a"])
def test_custom_float_bad(num):
    custom_floating = custom_float(num)
    assert isinstance(custom_floating, float)
    assert np.isnan(custom_floating)
