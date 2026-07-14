from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st


# ==========================================================
# Project Paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"


# ==========================================================
# Database Connection
# ==========================================================

def get_connection():

    return sqlite3.connect(DB_PATH)


# ==========================================================
# Companies
# ==========================================================

@st.cache_data(ttl=600)

def get_companies():

    conn = get_connection()

    df = pd.read_sql(

        """
        SELECT *
        FROM companies
        ORDER BY company_name
        """,

        conn

    )

    conn.close()

    return df


# ==========================================================
# Financial Ratios
# ==========================================================

@st.cache_data(ttl=600)

def get_ratios(

    ticker,

    year=None

):

    conn = get_connection()

    if year is None:

        query = """

        SELECT *

        FROM financial_ratios

        WHERE company_id=?

        ORDER BY id DESC

        """

        df = pd.read_sql(

            query,

            conn,

            params=(ticker,)

        )

    else:

        query = """

        SELECT *

        FROM financial_ratios

        WHERE company_id=?

        AND year=?

        """

        df = pd.read_sql(

            query,

            conn,

            params=(ticker, year)

        )

    conn.close()

    return df


# ==========================================================
# Profit & Loss
# ==========================================================

@st.cache_data(ttl=600)

def get_pl(ticker):

    conn = get_connection()

    df = pd.read_sql(

        """

        SELECT *

        FROM profit_loss

        WHERE company_id=?

        ORDER BY id

        """,

        conn,

        params=(ticker,)

    )

    conn.close()

    return df


# ==========================================================
# Balance Sheet
# ==========================================================

@st.cache_data(ttl=600)

def get_bs(ticker):

    conn = get_connection()

    df = pd.read_sql(

        """

        SELECT *

        FROM balance_sheet

        WHERE company_id=?

        ORDER BY id

        """,

        conn,

        params=(ticker,)

    )

    conn.close()

    return df


# ==========================================================
# Cash Flow
# ==========================================================

@st.cache_data(ttl=600)

def get_cf(ticker):

    conn = get_connection()

    df = pd.read_sql(

        """

        SELECT *

        FROM cash_flow

        WHERE company_id=?

        ORDER BY id

        """,

        conn,

        params=(ticker,)

    )

    conn.close()

    return df
# ==========================================================
# Sector Information
# ==========================================================

@st.cache_data(ttl=600)
def get_sectors():

    conn = get_connection()

    try:

        df = pd.read_sql(

            """
            SELECT *
            FROM sectors
            ORDER BY broad_sector
            """,

            conn

        )

    finally:

        conn.close()

    return df


# ==========================================================
# Peer Groups
# ==========================================================

@st.cache_data(ttl=600)
def get_peers(group_name):

    conn = get_connection()

    try:

        query = """

        SELECT *

        FROM peer_percentiles

        WHERE peer_group_name=?

        ORDER BY company_id

        """

        df = pd.read_sql(

            query,

            conn,

            params=(group_name,)

        )

    finally:

        conn.close()

    return df


# ==========================================================
# Valuation
# ==========================================================

@st.cache_data(ttl=600)
def get_valuation(ticker):

    conn = get_connection()

    try:

        tables = pd.read_sql(

            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            """,

            conn

        )["name"].tolist()

        if "valuation" not in tables:

            return pd.DataFrame()

        df = pd.read_sql(

            """

            SELECT *

            FROM valuation

            WHERE company_id=?

            """,

            conn,

            params=(ticker,)

        )

    finally:

        conn.close()

    return df


# ==========================================================
# Available Years
# ==========================================================

@st.cache_data(ttl=600)
def get_available_years():

    conn = get_connection()

    try:

        df = pd.read_sql(

            """

            SELECT DISTINCT year

            FROM financial_ratios

            ORDER BY year

            """,

            conn

        )

    finally:

        conn.close()

    return df["year"].tolist()


# ==========================================================
# Peer Groups List
# ==========================================================

@st.cache_data(ttl=600)
def get_peer_groups():

    conn = get_connection()

    try:

        df = pd.read_sql(

            """

            SELECT DISTINCT peer_group_name

            FROM peer_percentiles

            ORDER BY peer_group_name

            """,

            conn

        )

    finally:

        conn.close()

    return df["peer_group_name"].tolist()


# ==========================================================
# Safe Query Wrapper
# ==========================================================

def safe_query(function, *args, **kwargs):

    try:

        return function(*args, **kwargs)

    except Exception as e:

        st.error(f"Database Error: {e}")

        return pd.DataFrame()