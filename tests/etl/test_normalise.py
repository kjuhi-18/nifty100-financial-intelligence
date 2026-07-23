import pytest
import numpy as np

from src.etl.normaliser import normalize_year


# --------------------------------------------------
# Mar-24 -> 2024-03
# --------------------------------------------------

def test_mar24():
    assert normalize_year("Mar-24") == "2024-03"


def test_dec12():
    assert normalize_year("Dec-12") == "2012-12"


def test_jan30():
    assert normalize_year("Jan-30") == "2030-01"


def test_dec99():
    assert normalize_year("Dec-99") == "1999-12"


# --------------------------------------------------
# Month Year
# --------------------------------------------------

def test_mar2024():
    assert normalize_year("Mar 2024") == "2024-03"


def test_dec2012():
    assert normalize_year("Dec 2012") == "2012-12"


def test_jul2018():
    assert normalize_year("Jul 2018") == "2018-07"


# --------------------------------------------------
# Year only
# --------------------------------------------------

def test_year_only():
    assert normalize_year("2024") == "2024-03"


def test_float_year():
    assert normalize_year("2024.5") == "2024-03"


# --------------------------------------------------
# Embedded year
# --------------------------------------------------

def test_mar2016_9m():
    assert normalize_year("Mar 2016 9m") == "2016-03"


# --------------------------------------------------
# TTM
# --------------------------------------------------

def test_ttm():
    assert normalize_year("TTM") is None


def test_ttm_lower():
    assert normalize_year("ttm") is None


# --------------------------------------------------
# Null values
# --------------------------------------------------

def test_none():
    assert normalize_year(None) is None


def test_nan():
    assert normalize_year(np.nan) is None


# --------------------------------------------------
# Whitespace
# --------------------------------------------------

def test_spaces():
    assert normalize_year("  Mar-24  ") == "2024-03"


# --------------------------------------------------
# Invalid values
# --------------------------------------------------

def test_invalid_string():
    assert normalize_year("Hello") == "Hello"


def test_random_text():
    assert normalize_year("abcdef") == "abcdef"


# --------------------------------------------------
# Invalid month
# --------------------------------------------------

def test_invalid_month():

    with pytest.raises(ValueError):
        normalize_year("Abc-24")


# --------------------------------------------------
# Boundary year
# --------------------------------------------------

def test_year_31():
    assert normalize_year("Jan-31") == "1931-01"


def test_year_00():
    assert normalize_year("Jan-00") == "2000-01"