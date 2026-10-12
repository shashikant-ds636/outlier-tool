# Outlier Tool

A beginner-friendly Python package for detecting and handling numeric outliers
using the IQR and Z-score methods.

## Installation

From a wheel file (any device):

```bash
python -m pip install outlier_tool_shashikant-0.1.0-py3-none-any.whl
```

From GitHub:

```bash
python -m pip install git+https://github.com/YOUR_USERNAME/outlier-tool.git
```

## Quick start

```python
import pandas as pd
from outlier_tool import Outliers

df = pd.read_csv("data.csv")
o = Outliers(df)                       # or Outliers(df, columns=["price", "age"])

print(o.find("iqr"))                   # summary table
print(o.find("zscore"))

df1 = o.iqr_trim()                     # remove rows
df2 = o.iqr_cap()                      # cap values
df3 = o.zscore_trim(limit=3)
df4 = o.zscore_cap(limit=2.5)
df5 = o.replace_with_mean("iqr")
df6 = o.replace_with_median("zscore")
```

## Methods

| Method | Purpose |
|---|---|
| `find(method, threshold)` | Summary of outliers per column |
| `iqr_trim(factor=1.5)` | Remove rows with IQR outliers |
| `iqr_cap(factor=1.5)` | Cap values at IQR limits |
| `zscore_trim(limit=3)` | Remove rows with Z-score outliers |
| `zscore_cap(limit=3)` | Cap values at Z-score limits |
| `replace_with_mean(method, threshold)` | Replace outliers with the mean of non-outliers |
| `replace_with_median(method, threshold)` | Replace outliers with the median of non-outliers |

## Important notes

- Outliers are not always errors. Look at them before removing them.
- Trimming removes the whole row if any checked column has an outlier.
- Every method returns a new DataFrame; your original data is unchanged.
- Missing values (NaN) are never flagged as outliers.
- Constant columns (std = 0) are skipped by the Z-score method.
- For machine learning, calculate limits on training data only.

## License

MIT
