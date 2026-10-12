import numpy as np
import pandas as pd
import pytest
from outlier_tool import Outliers


def sample_data():
    return pd.DataFrame({
        "amount": [10, 11, 12, 13, 14, 15, 16, 500],
        "age": [20, 21, 22, 23, 24, 25, 26, 27],
    })


def test_find_returns_summary():
    report = Outliers(sample_data()).find("iqr")
    assert {"column", "outliers", "lower", "upper"} <= set(report.columns)
    assert len(report) == 2
    assert report.loc[report.column == "amount", "outliers"].iloc[0] == 1


def test_capping_keeps_row_count_and_limits_value():
    df = sample_data()
    result = Outliers(df).iqr_cap()
    assert len(result) == len(df)
    assert result["amount"].max() < 500


def test_trimming_removes_outlier_row():
    result = Outliers(sample_data()).iqr_trim()
    assert len(result) == 7
    assert 500 not in result["amount"].values


def test_original_dataframe_is_unchanged():
    df = sample_data()
    o = Outliers(df)
    o.iqr_cap(); o.iqr_trim(); o.replace_with_mean()
    assert df["amount"].max() == 500
    assert o.df["amount"].max() == 500


def test_zscore_methods_run():
    df = pd.DataFrame({"x": list(range(1, 30)) + [1000]})
    o = Outliers(df)
    assert o.find("zscore")["outliers"].iloc[0] == 1
    assert len(o.zscore_trim()) == 29
    assert o.zscore_cap()["x"].max() < 1000


def test_replace_with_mean_and_median():
    o = Outliers(sample_data())
    assert o.replace_with_mean()["amount"].max() < 500
    assert o.replace_with_median()["amount"].max() < 500


def test_invalid_column_raises():
    with pytest.raises(KeyError):
        Outliers(sample_data(), columns=["nope"])


def test_empty_columns_list_selects_nothing():
    assert Outliers(sample_data(), columns=[]).num_cols == []


def test_constant_column_has_no_outliers():
    df = pd.DataFrame({"c": [5, 5, 5, 5]})
    assert Outliers(df).find("zscore")["outliers"].iloc[0] == 0


def test_nan_is_not_flagged():
    df = pd.DataFrame({"x": [1, 2, 3, 4, np.nan, 5]})
    assert Outliers(df).find("iqr")["outliers"].iloc[0] == 0


def test_bad_method_raises():
    with pytest.raises(ValueError):
        Outliers(sample_data()).find("bad")
