# Changelog

All notable changes to `outlier-tool-shashikant` are documented here.

## [0.2.0]

### Added
- **Series support.** `Outliers(data)` now accepts a `pandas.Series` directly, in addition
  to a `pandas.DataFrame`. All existing detection and handling methods
  (`find`, `iqr_trim`, `iqr_cap`, `zscore_trim`, `zscore_cap`, `replace_with_mean`,
  `replace_with_median`) work the same way on a Series.
  - Handling methods return a `pandas.Series` (preserving its `name` and the index
    labels of retained elements) instead of a DataFrame.
  - `find()` returns a one-row report for a Series.
  - The original Series is never modified.
  - `columns=` cannot be combined with Series input and raises `ValueError`.

### Changed
- `Outliers.__init__` now validates and routes input type (`DataFrame` vs `Series`) before
  doing any other setup. Passing anything else (list, dict, scalar, ...) still raises
  `TypeError`, as before.
- Internal calculation logic (`_iqr_bounds`, `_zscore_bounds`, `_outlier_mask`, `_trim`,
  `_cap`) is now shared between DataFrame and Series input instead of being duplicated.

### Unchanged
- Public API, method names, and default parameter values for DataFrame usage are
  unchanged from 0.1.x. Existing DataFrame code continues to work without modification.
- Outlier calculation behavior (IQR bounds, Z-score bounds, NaN handling, constant-column
  handling) is unchanged.

## [0.1.1]
- Initial IQR/Z-score detection, trimming, capping, and mean/median replacement for
  `pandas.DataFrame` input.
