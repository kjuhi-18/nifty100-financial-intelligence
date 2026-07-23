import pandas as pd
import pytest
from pathlib import Path

from src.etl.loader import ExcelLoader


# --------------------------------------------------
# Helper
# --------------------------------------------------

def create_excel(tmp_path, filename, df):
    file_path = tmp_path / filename
    df.to_excel(file_path, index=False)
    return file_path


# --------------------------------------------------
# 1. File exists
# --------------------------------------------------

def test_load_excel_success(tmp_path):

    df = pd.DataFrame({
        "A": [1, 2],
        "B": [3, 4]
    })

    create_excel(tmp_path, "sample.xlsx", df)

    loader = ExcelLoader(tmp_path)

    loaded = loader.load_excel("sample.xlsx", header=0)

    assert len(loaded) == 2


# --------------------------------------------------
# 2. Missing file
# --------------------------------------------------

def test_missing_file(tmp_path):

    loader = ExcelLoader(tmp_path)

    with pytest.raises(FileNotFoundError):
        loader.load_excel("missing.xlsx")


# --------------------------------------------------
# 3. Column names
# --------------------------------------------------

def test_column_names(tmp_path):

    df = pd.DataFrame({
        "company": [1],
        "sales": [100]
    })

    create_excel(tmp_path, "companies.xlsx", df)

    loader = ExcelLoader(tmp_path)

    loaded = loader.load_excel("companies.xlsx", header=0)

    assert list(loaded.columns) == [
        "company",
        "sales"
    ]


# --------------------------------------------------
# 4. Row count
# --------------------------------------------------

def test_row_count(tmp_path):

    df = pd.DataFrame({
        "A": range(5)
    })

    create_excel(tmp_path, "rows.xlsx", df)

    loader = ExcelLoader(tmp_path)

    loaded = loader.load_excel("rows.xlsx", header=0)

    assert len(loaded) == 5


# --------------------------------------------------
# 5. Empty file
# --------------------------------------------------

def test_empty_file(tmp_path):

    df = pd.DataFrame(columns=["A"])

    create_excel(tmp_path, "empty.xlsx", df)

    loader = ExcelLoader(tmp_path)

    loaded = loader.load_excel("empty.xlsx", header=0)

    assert loaded.empty


# --------------------------------------------------
# 6. load_all returns dict
# --------------------------------------------------

def test_load_all_returns_dict(tmp_path):

    create_excel(tmp_path, "a.xlsx", pd.DataFrame({"A": [1]}))
    create_excel(tmp_path, "b.xlsx", pd.DataFrame({"B": [2]}))

    loader = ExcelLoader(tmp_path)

    data = loader.load_all([
        "a.xlsx",
        "b.xlsx"
    ])

    assert isinstance(data, dict)


# --------------------------------------------------
# 7. load_all keys
# --------------------------------------------------

def test_load_all_keys(tmp_path):

    create_excel(tmp_path, "a.xlsx", pd.DataFrame({"A":[1]}))
    create_excel(tmp_path, "b.xlsx", pd.DataFrame({"B":[2]}))

    loader = ExcelLoader(tmp_path)

    data = loader.load_all([
        "a.xlsx",
        "b.xlsx"
    ])

    assert "a.xlsx" in data
    assert "b.xlsx" in data


# --------------------------------------------------
# 8. First dataframe shape
# --------------------------------------------------

def test_first_dataframe_shape(tmp_path):

    create_excel(
        tmp_path,
        "a.xlsx",
        pd.DataFrame({
            "A":[1,2,3]
        })
    )

    loader = ExcelLoader(tmp_path)

    df = loader.load_excel("a.xlsx", header=0)

    assert df.shape == (3,1)


# --------------------------------------------------
# 9. Second dataframe shape
# --------------------------------------------------

def test_second_dataframe_shape(tmp_path):

    create_excel(
        tmp_path,
        "b.xlsx",
        pd.DataFrame({
            "A":[1],
            "B":[2]
        })
    )

    loader = ExcelLoader(tmp_path)

    df = loader.load_excel("b.xlsx", header=0)

    assert df.shape == (1,2)


# --------------------------------------------------
# 10. Data preserved
# --------------------------------------------------

def test_loaded_values(tmp_path):

    df = pd.DataFrame({
        "sales":[100,200]
    })

    create_excel(tmp_path, "values.xlsx", df)

    loader = ExcelLoader(tmp_path)

    loaded = loader.load_excel(
        "values.xlsx",
        header=0
    )

    assert loaded.iloc[1]["sales"] == 200