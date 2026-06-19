import pytest

from src.etl.normaliser import (
    normalize_ticker,
    normalize_year
)

@pytest.mark.parametrize(
    "input_ticker,expected",
    [
        ("TCS", "TCS"),
        ("tcs", "TCS"),
        (" tcs ", "TCS"),
        ("INFY", "INFY"),
        ("infy", "INFY"),
        (" HDFCBANK ", "HDFCBANK"),
        ("itc", "ITC"),
        ("SBIN", "SBIN"),
        ("reliance", "RELIANCE"),
        ("LT", "LT"),
        ("asianpaint", "ASIANPAINT"),
        ("bajfinance", "BAJFINANCE"),
        ("tatamotors", "TATAMOTORS"),
        ("nestleind", "NESTLEIND"),
        ("sunpharma", "SUNPHARMA"),
    ]
)
def test_normalize_ticker(input_ticker, expected):
    assert normalize_ticker(input_ticker) == expected


@pytest.mark.parametrize(
    "raw_year,expected",
    [
        ("Mar-10", "2010-03"),
        ("Mar-11", "2011-03"),
        ("Mar-12", "2012-03"),
        ("Mar-13", "2013-03"),
        ("Mar-14", "2014-03"),
        ("Mar-15", "2015-03"),
        ("Mar-16", "2016-03"),
        ("Mar-17", "2017-03"),
        ("Mar-18", "2018-03"),
        ("Mar-19", "2019-03"),
        ("Mar-20", "2020-03"),
        ("Mar-21", "2021-03"),
        ("Mar-22", "2022-03"),
        ("Mar-23", "2023-03"),
        ("Mar-24", "2024-03"),
        ("Mar-25", "2025-03"),
        ("Mar-26", "2026-03"),
        ("Mar-27", "2027-03"),
        ("Mar-28", "2028-03"),
        ("Mar-29", "2029-03"),
    ]
)
def test_normalize_year(raw_year, expected):
    assert normalize_year(raw_year) == expected
def test_year_only_format():
    assert normalize_year("2024") == "2024-03"


def test_invalid_month():
    with pytest.raises(ValueError):
        normalize_year("ABC-24")
