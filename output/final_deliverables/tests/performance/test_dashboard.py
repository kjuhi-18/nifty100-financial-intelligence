import time

from src.dashboard.utils.db import get_bs, get_cf, get_pl, get_ratios

TICKERS = ["TCS", "INFY", "RELIANCE", "HDFCBANK", "SBIN"]


def test_company_profile_load():
    for ticker in TICKERS:
        start = time.perf_counter()

        get_ratios(ticker)
        get_pl(ticker)
        get_bs(ticker)
        get_cf(ticker)

        elapsed = time.perf_counter() - start

        print(f"{ticker}: {elapsed:.3f}s")

        assert elapsed < 3
