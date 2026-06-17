import re
import pandas as pd
import numpy as np


def normalize_ticker(ticker: str) -> str:
    """
    Convert ticker to standardized NSE format.

    Examples:
    ' tcs ' -> 'TCS'
    'hdfcbank' -> 'HDFCBANK'
    """

    if pd.isna(ticker):
        return None

    ticker = str(ticker).strip().upper()

    return ticker


def normalize_year(year_value: str) -> str:
    """
    Convert:
    Mar-24 -> 2024-03
    Mar-23 -> 2023-03
    Mar-10 -> 2010-03
    """

    if pd.isna(year_value):
        return None

    year_value = str(year_value).strip()

    match = re.match(r"([A-Za-z]{3})-(\d{2})$", year_value)

    if not match:
        raise ValueError(f"Invalid year format: {year_value}")

    month_str, year_suffix = match.groups()

    month_map = {
        "Jan": "01",
        "Feb": "02",
        "Mar": "03",
        "Apr": "04",
        "May": "05",
        "Jun": "06",
        "Jul": "07",
        "Aug": "08",
        "Sep": "09",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12"
    }

    month = month_map.get(month_str)

    if month is None:
        raise ValueError(f"Invalid month: {month_str}")

    year_num = int(year_suffix)

    if year_num <= 30:
        year = 2000 + year_num
    else:
        year = 1900 + year_num

    return f"{year}-{month}"


def clean_numeric(value):
    """
    Clean numeric fields.

    Examples:
    12,345 -> 12345
    '1,234.56' -> 1234.56
    """

    if pd.isna(value):
        return np.nan

    value = str(value).replace(",", "").strip()

    if value == "":
        return np.nan

    return float(value)


def clean_text(value):
    """
    Remove newlines and extra spaces.
    """

    if pd.isna(value):
        return None

    value = str(value)

    value = value.replace("\n", " ")
    value = re.sub(r"\s+", " ", value)

    return value.strip()