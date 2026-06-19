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


import pandas as pd
import re


def normalize_year(year_value):
    if "TTM" in year_value.upper():
        return None

    if pd.isna(year_value):
        return None

    year_value = str(year_value).strip()

    # Format: Mar-24
    match1 = re.match(
        r"([A-Za-z]{3})-(\d{2})$",
        year_value
    )

    if match1:

        month_str, year_suffix = match1.groups()
        

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
        if month_str not in month_map:
            raise ValueError(
            f"Invalid month format: {month_str}"
        )

        year_num = int(year_suffix)

        if year_num <= 30:
            year = 2000 + year_num
        else:
            year = 1900 + year_num

        return f"{year}-{month_map[month_str]}"

    # Format: Dec 2012
    match2 = re.match(
        r"([A-Za-z]{3})\s+(\d{4})$",
        year_value
    )

    if match2:

        month_str, year = match2.groups()

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

        return f"{year}-{month_map[month_str]}"
        match3 = re.search(r"(20\d{2})", year_value)

        if match3:
            return f"{match3.group(1)}-03"
    # Format: Mar 2013
    match4 = re.match(
    r"([A-Za-z]{3})\s+(\d{4})$",
    year_value
    )

    if match4:
        month, year = match4.groups()

        month_map = {
        "Jan":"01","Feb":"02","Mar":"03",
        "Apr":"04","May":"05","Jun":"06",
        "Jul":"07","Aug":"08","Sep":"09",
        "Oct":"10","Nov":"11","Dec":"12"
        }

        return f"{year}-{month_map[month]}"
    # Format: 2013
    if re.match(r"^\d{4}$", year_value):
        return f"{year_value}-03"
    # Format: 2024.5
    match5 = re.match(r"^(\d{4})\.\d+$", year_value)

    if match5:
        return f"{match5.group(1)}-03"
    # Format: Mar 2016 9m
    match6 = re.search(r"(20\d{2})", year_value)

    if match6:
        return f"{match6.group(1)}-03"
    return year_value

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