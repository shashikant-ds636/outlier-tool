<p align="center">
  <img src="https://raw.githubusercontent.com/shashikant-ds636/outlier-tool/main/assets/logo.png" alt="Outlier Tool logo" width="640">
</p>

<p align="center">
  <a href="https://pypi.org/project/outlier-tool-shashikant/"><img src="https://img.shields.io/pypi/v/outlier-tool-shashikant?color=2dd4bf&label=PyPI" alt="PyPI version"></a>
  <img src="https://img.shields.io/pypi/pyversions/outlier-tool-shashikant?color=60a5fa" alt="Python versions">
  <img src="https://img.shields.io/badge/license-MIT-f87171" alt="MIT license">
  <a href="https://colab.research.google.com/#create=true"><img src="https://img.shields.io/badge/Open%20in-Colab-F9AB00?logo=googlecolab&logoColor=white" alt="Open in Colab"></a>
</p>

<p align="center">
  A beginner-friendly Python package for <b>detecting</b> and <b>handling</b> numeric outliers
  with the <b>IQR</b> and <b>Z-score</b> methods.
</p>

---

## Table of contents

- [Features](#-features)
- [Installation](#-installation)
- [Use it in Google Colab](#-use-it-in-google-colab)
- [Quick start](#-quick-start)
- [Methods](#-methods)
- [How the two methods work](#-how-the-two-methods-work)
- [Which handling method should I use?](#-which-handling-method-should-i-use)
- [Important notes](#-important-notes)
- [Author and license](#-author-and-license)

## ✨ Features

- 🔍 **Find** outliers in every numeric column with one call
- 📏 Two detection methods: **IQR** and **Z-score**
- ✂️ **Trim** (remove rows), 🧢 **cap** (clip values) or 🔁 **replace** (mean / median)
- 🎯 Choose which columns to check
- 🛡️ Never changes your original DataFrame, because every method returns a new one

## 📦 Installation

**From PyPI (recommended):**

```bash
python -m pip install outlier-tool-shashikant
```

**From GitHub (latest code):**

```bash
python -m pip install git+https://github.com/shashikant-ds636/outlier-tool.git
```

**From a wheel file (offline or another device):**

```bash
python -m pip install outlier_tool_shashikant-0.1.0-py3-none-any.whl
```

**Upgrade to the newest version:**

```bash
python -m pip install --upgrade outlier-tool-shashikant
```

> Requires Python 3.9+, `numpy` and `pandas` (installed automatically).

## 🚀 Use it in Google Colab

Colab does not keep installed packages between sessions, so run the install cell **at the top of your notebook every time**.

**Step 1. Install (first cell)**

```python
!pip install -q outlier-tool-shashikant
```

Or install the latest code from GitHub:

```python
!pip install -q git+https://github.com/shashikant-ds636/outlier-tool.git
```

**Step 2. Import and run (next cell)**

```python
import pandas as pd
from outlier_tool import Outliers

# Option A: upload your own CSV
from google.colab import files
uploaded = files.upload()
df = pd.read_csv(next(iter(uploaded)))

# Option B: read from Google Drive
# from google.colab import drive
# drive.mount("/content/drive")
# df = pd.read_csv("/content/drive/MyDrive/your_file.csv")

o = Outliers(df)
print(o.find("iqr"))
df_clean = o.iqr_cap()
df_clean.head()
```

**No data handy? Try this copy-paste demo:**

```python
import pandas as pd
from outlier_tool import Outliers

df = pd.DataFrame({
    "price": [10, 12, 11, 13, 12, 14, 11, 500],
    "age":   [21, 22, 23, 24, 25, 26, 27, 28],
})

o = Outliers(df)
print(o.find("iqr"))       # shows 1 outlier in "price"
print(o.iqr_cap())         # 500 is capped to the upper limit
```

> If Colab says `ModuleNotFoundError`, run the install cell again, then **Runtime → Restart session** and re-run your cells.

## ⚡ Quick start

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

For the demo data above, `find("iqr")` returns:

| column | method | lower | upper | outliers | percent |
|---|---|---|---|---|---|
| price | iqr | 7.625 | 16.625 | 1 | 12.5 |
| age | iqr | 17.5 | 31.5 | 0 | 0.0 |

## 🧰 Methods

| Method | What it does |
|---|---|
| `Outliers(df, columns=None)` | Create the tool. `columns` limits which columns are checked |
| `find(method="iqr", threshold=None)` | Summary of outliers per column (`"iqr"` or `"zscore"`) |
| `iqr_trim(factor=1.5)` | Remove rows with IQR outliers |
| `iqr_cap(factor=1.5)` | Cap values at the IQR limits |
| `zscore_trim(limit=3)` | Remove rows with Z-score outliers |
| `zscore_cap(limit=3)` | Cap values at the Z-score limits |
| `replace_with_mean(method="iqr", threshold=None)` | Replace outliers with the mean of the non-outliers |
| `replace_with_median(method="iqr", threshold=None)` | Replace outliers with the median of the non-outliers |

## 📐 How the two methods work

| | IQR method | Z-score method |
|---|---|---|
| **Idea** | Uses the middle 50% of the data | Uses the mean and standard deviation |
| **Lower limit** | `Q1 - 1.5 × IQR` | `mean - 3 × std` |
| **Upper limit** | `Q3 + 1.5 × IQR` | `mean + 3 × std` |
| **Best for** | Skewed data (salary, price, sales) | Roughly bell-shaped data |
| **Weakness** | Can flag many points in small datasets | Big outliers inflate the mean and std |

Here `IQR = Q3 - Q1`. A value outside the lower and upper limits is flagged as an outlier.

## 🧭 Which handling method should I use?

| Goal | Use | Keeps all rows? |
|---|---|---|
| Outliers are mistakes and rows are not needed | `*_trim` | ❌ No |
| Real values, but extreme. Keep the rows, limit the impact | `*_cap` | ✅ Yes |
| Want a typical value in place of the outlier | `replace_with_mean` / `replace_with_median` | ✅ Yes |

## ⚠️ Important notes

- Outliers are **not always errors**. Look at them before removing them.
- Trimming removes the **whole row** if any checked column has an outlier.
- Every method returns a **new DataFrame**. Save it, for example `df_clean = o.iqr_cap()`.
- Missing values (NaN) are never flagged as outliers.
- Constant columns (std = 0) are skipped by the Z-score method.
- Skip ID columns and 0/1 flag columns with `Outliers(df, columns=[...])`.
- For machine learning, calculate the limits on the **training data only** to avoid data leakage.

## 👤 Author and license

Made by **Shashikant** · [GitHub](https://github.com/shashikant-ds636) · [Portfolio](https://shashikantgiri.netlify.app)

Found a bug or have an idea? [Open an issue](https://github.com/shashikant-ds636/outlier-tool/issues).

Released under the **MIT License**.
