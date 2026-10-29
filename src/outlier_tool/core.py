import numpy as np
import pandas as pd


class Outliers:
    def __init__(self, data, columns=None):
        """
        data    : a pandas DataFrame or a pandas Series
        columns : list of columns to check (DataFrame only; default = all
                  numeric columns). Must be None for Series input.
        """
        if isinstance(data, pd.Series):
            if columns is not None:
                raise ValueError("columns is not supported when data is a pandas Series")
            if not pd.api.types.is_numeric_dtype(data):
                raise ValueError("Series must be numeric")

            self._is_series = True
            self._series_name = data.name
            col_name = data.name if data.name is not None else "value"
            self._col_name = col_name
            self.df = data.rename(col_name).to_frame()
            self.num_cols = [col_name]
            return

        if not isinstance(data, pd.DataFrame):
            raise TypeError("data must be a pandas DataFrame or a pandas Series")

        self._is_series = False
        self.df = data.copy()
        numeric = self.df.select_dtypes(include=np.number).columns.tolist()

        if columns is None:
            self.num_cols = numeric
        else:
            columns = list(columns)
            missing = [c for c in columns if c not in self.df.columns]
            if missing:
                raise KeyError(f"Columns not found: {missing}")
            not_numeric = [c for c in columns if c not in numeric]
            if not_numeric:
                raise ValueError(f"Columns are not numeric: {not_numeric}")
            self.num_cols = columns

    # ---------- output helpers ----------
    def _wrap(self, result_df):
        """Convert an internal result DataFrame back to a Series when the
        tool was constructed from a Series; otherwise return it as-is."""
        if self._is_series:
            return result_df[self._col_name].rename(self._series_name)
        return result_df

    # ---------- 1. LIMITS ----------
    def _iqr_bounds(self, col, factor=1.5):
        Q1 = self.df[col].quantile(0.25)
        Q3 = self.df[col].quantile(0.75)
        IQR = Q3 - Q1
        return Q1 - factor * IQR, Q3 + factor * IQR

    def _zscore_bounds(self, col, limit=3):
        mean = self.df[col].mean()
        std = self.df[col].std()
        # constant column (std = 0) or single value (std = NaN): nothing is flagged
        if pd.isna(std) or std == 0:
            return -np.inf, np.inf
        return mean - limit * std, mean + limit * std

    def _bounds(self, col, method, threshold):
        if method == "iqr":
            if threshold is not None and not isinstance(threshold, (int, float)):
                raise ValueError("threshold/factor must be numeric")
            return self._iqr_bounds(col, threshold if threshold is not None else 1.5)
        if method == "zscore":
            if threshold is not None and not isinstance(threshold, (int, float)):
                raise ValueError("threshold/limit must be numeric")
            return self._zscore_bounds(col, threshold if threshold is not None else 3)
        raise ValueError("method must be 'iqr' or 'zscore'")

    def _outlier_mask(self, method, threshold):
        """True/False table: True = this value is an outlier (NaN is never flagged)."""
        mask = pd.DataFrame(False, index=self.df.index, columns=self.num_cols)
        for col in self.num_cols:
            lower, upper = self._bounds(col, method, threshold)
            mask[col] = (self.df[col] < lower) | (self.df[col] > upper)
        return mask

    # ---------- 2. FIND OUTLIERS ----------
    def find(self, method="iqr", threshold=None):
        """Summary table of outliers per column (one row per column; one
        row total when the tool was constructed from a Series)."""
        rows = []
        for col in self.num_cols:
            lower, upper = self._bounds(col, method, threshold)
            n = int(((self.df[col] < lower) | (self.df[col] > upper)).sum())
            label = self._series_name if (self._is_series and self._series_name is not None) else col
            rows.append({
                "column": label, "method": method,
                "lower": lower, "upper": upper,
                "outliers": n,
                "percent": round(n / len(self.df) * 100, 2) if len(self.df) else 0.0,
            })
        return pd.DataFrame(rows)

    # ---------- 3. TRIM and CAP (generic) ----------
    def _trim(self, method, threshold):
        mask = self._outlier_mask(method, threshold)
        return self.df[~mask.any(axis=1)]  # drops the whole row if any column has an outlier

    def _cap(self, method, threshold):
        out = self.df.copy()
        for col in self.num_cols:
            lower, upper = self._bounds(col, method, threshold)
            out[col] = out[col].clip(lower, upper)
        return out

    # ---------- 4. IQR METHOD ----------
    def iqr_trim(self, factor=1.5):
        """IQR + TRIM: remove rows/elements with outliers."""
        return self._wrap(self._trim("iqr", factor))

    def iqr_cap(self, factor=1.5):
        """IQR + CAPPING: replace outliers with lower/upper limit."""
        return self._wrap(self._cap("iqr", factor))

    # ---------- 5. Z-SCORE METHOD ----------
    def zscore_trim(self, limit=3):
        """Z-score + TRIM: remove rows/elements with outliers."""
        return self._wrap(self._trim("zscore", limit))

    def zscore_cap(self, limit=3):
        """Z-score + CAPPING: replace outliers with lower/upper limit."""
        return self._wrap(self._cap("zscore", limit))

    # ---------- 6. REPLACE WITH MEAN / MEDIAN ----------
    def replace_with_mean(self, method="iqr", threshold=None):
        """Replace outliers with the column mean (calculated without the outliers)."""
        out = self.df.copy()
        mask = self._outlier_mask(method, threshold)
        for col in self.num_cols:
            if mask[col].any():
                out.loc[mask[col], col] = self.df.loc[~mask[col], col].mean()
        return self._wrap(out)

    def replace_with_median(self, method="iqr", threshold=None):
        """Replace outliers with the column median (calculated without the outliers)."""
        out = self.df.copy()
        mask = self._outlier_mask(method, threshold)
        for col in self.num_cols:
            if mask[col].any():
                out.loc[mask[col], col] = self.df.loc[~mask[col], col].median()
        return self._wrap(out)
