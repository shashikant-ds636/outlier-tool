import numpy as np
import pandas as pd


class Outliers:
    def __init__(self, df, columns=None):
        """
        df      : your DataFrame
        columns : list of columns to check (default = all numeric columns)
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")

        self.df = df.copy()
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
            return self._iqr_bounds(col, threshold if threshold is not None else 1.5)
        if method == "zscore":
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
        """Summary table of outliers per column."""
        rows = []
        for col in self.num_cols:
            lower, upper = self._bounds(col, method, threshold)
            n = int(((self.df[col] < lower) | (self.df[col] > upper)).sum())
            rows.append({
                "column": col, "method": method,
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
        """IQR + TRIM: remove rows with outliers."""
        return self._trim("iqr", factor)

    def iqr_cap(self, factor=1.5):
        """IQR + CAPPING: replace outliers with lower/upper limit."""
        return self._cap("iqr", factor)

    # ---------- 5. Z-SCORE METHOD ----------
    def zscore_trim(self, limit=3):
        """Z-score + TRIM: remove rows with outliers."""
        return self._trim("zscore", limit)

    def zscore_cap(self, limit=3):
        """Z-score + CAPPING: replace outliers with lower/upper limit."""
        return self._cap("zscore", limit)

    # ---------- 6. REPLACE WITH MEAN / MEDIAN ----------
    def replace_with_mean(self, method="iqr", threshold=None):
        """Replace outliers with the column mean (calculated without the outliers)."""
        out = self.df.copy()
        mask = self._outlier_mask(method, threshold)
        for col in self.num_cols:
            if mask[col].any():
                out.loc[mask[col], col] = self.df.loc[~mask[col], col].mean()
        return out

    def replace_with_median(self, method="iqr", threshold=None):
        """Replace outliers with the column median (calculated without the outliers)."""
        out = self.df.copy()
        mask = self._outlier_mask(method, threshold)
        for col in self.num_cols:
            if mask[col].any():
                out.loc[mask[col], col] = self.df.loc[~mask[col], col].median()
        return out
