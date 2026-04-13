# Computational Methods Reference

ALWAYS call `python3 /app/toolkit.py <command> '<json>'` for calculations.

## Percent Change
**Triggers:** "percent change", "percentage change", "how much did X change", "growth rate" (simple, not compound)
**Formula:** `|new − old| / old × 100` (denominator = the OLD/BASE value)
```bash
python3 /app/toolkit.py percent_change '{"old": 1234, "new": 5678}'
# Returns absolute % change. Add "absolute": false for signed.
```

## Percent Difference ← DIFFERENT from Percent Change!
**Triggers:** "percent difference", "absolute percent difference", "how much do these two values differ"
**Formula:** `|a − b| / ((a+b)/2) × 100` (denominator = AVERAGE of both — symmetric)
```bash
python3 /app/toolkit.py percent_difference '{"a": 528, "b": 693}'
# Example: 528 vs 693 → 27.0  (NOT 31.25 — that would be percent change)
```
**CRITICAL:** `percent_change` and `percent_difference` give different answers. Use the right one.

## CAGR (Compound Annual Growth Rate)
**Triggers:** "CAGR", "compound annual growth", "annualized growth rate"
```bash
python3 /app/toolkit.py cagr '{"start_val": 100, "end_val": 200, "periods": 10}'
# Returns rate as %. "periods" = number of years/intervals.
```

## Theil Index
**Triggers:** "Theil index", "Theil measure", "dispersion", "inequality index"
```bash
python3 /app/toolkit.py theil_index '{"values": [12.3, 14.5, 13.2, 15.1]}'
```
Uses Theil-T (GE(1)): `(1/n) * sum(xi/mu * ln(xi/mu))`. All values must be **positive**.

## Hodrick-Prescott Filter
**Triggers:** "Hodrick-Prescott", "HP filter", "trend component", "structural balance", "cyclical component"
```bash
python3 /app/toolkit.py hp_filter '{"y": [100, 120, 110, 130, 125], "lamb": 100}'
# Returns {"trend": [...], "cycle": [...]}
```
- Use λ from the question. If not specified: 100 for annual, 1600 for quarterly.
- Cycle = original - trend (computed automatically).
- **NEVER implement HP filter in custom Python** — boundary conditions are complex and custom code gives wrong results. ALWAYS use the toolkit.
- **For FY receipts/outlays series:** Use the September bulletin's FD-1 or FD-5 summary table — it contains the complete historical annual series in one table. The September 2025 bulletin has FY2024 final data.

## Geometric Mean
**Triggers:** "geometric mean", "geometric average"
```bash
python3 /app/toolkit.py geometric_mean '{"values": [3.5, 4.2, 3.8]}'
```

## Euclidean Norm
**Triggers:** "Euclidean norm", "L2 norm", "magnitude", "Euclidean distance"
```bash
python3 /app/toolkit.py euclidean_norm '{"vector": [100, -200, 150]}'
```
For distance between two vectors: compute element-wise differences first, then pass as vector.

## Annualized Volatility
**Triggers:** "volatility", "realized volatility", "annualized volatility"
```bash
python3 /app/toolkit.py annualized_volatility '{"rates": [3.5, 3.6, 3.4, 3.7], "periods_per_year": 52}'
```
Computes: log returns → realized variance (mean of squared returns) → annualize → as %.
- Weekly data: `periods_per_year = 52`
- Monthly data: `periods_per_year = 12`
- Daily data: `periods_per_year = 252`

## Count Local Maxima / Minima
**Triggers:** "local maxima", "local minima", "peaks", "troughs", "how many times"
```bash
python3 /app/toolkit.py count_local_maxima '{"series": [1, 3, 2, 4, 1]}'
python3 /app/toolkit.py count_local_minima '{"series": [3, 1, 4, 2, 5]}'
```
Strict inequality. Boundary points (first/last) excluded.

## Arithmetic Mean
**Triggers:** "mean", "average", "arithmetic mean"
```bash
python3 /app/toolkit.py arithmetic_mean '{"values": [100, 200, 300]}'
```

## Absolute Difference
**Triggers:** "absolute difference", "difference between"
```bash
python3 /app/toolkit.py abs_diff '{"a": 100, "b": 75}'
```

## Parse Table
**For extracting structured data from pipe-delimited tables in the corpus:**
```bash
python3 /app/toolkit.py parse_table '{"text": "| Year | Val |\n|---|---|\n| 1960 | 12.3 |"}'
# Returns: [{"Year": "1960", "Val": "12.3"}]
```

## Standard Deviation & Coefficient of Variation
**Triggers:** "standard deviation", "population std dev", "price volatility" (non-annualized), "coefficient of variation", "CV", "volatility index"
```bash
# Population std dev (default, divide by N)
python3 /app/toolkit.py std_dev '{"values": [10, 20, 30]}'
# Sample std dev (divide by N-1)
python3 /app/toolkit.py std_dev '{"values": [10, 20, 30], "population": false}'
# CV = (population std / |mean|) × 100
python3 /app/toolkit.py coefficient_of_variation '{"values": [10, 20, 30]}'
# Returns: 40.825 (as percent)
```
**CRITICAL:** "population standard deviation" uses N denominator (default). "Sample" uses N-1. Use the correct one based on the question.

For "CV of year-to-year log growth rates":
```python
import math
values = [...]  # raw series
log_rates = [math.log(values[i]/values[i-1]) for i in range(1, len(values))]
# Then: python3 /app/toolkit.py coefficient_of_variation '{"values": [log_rates...]}'
```

## Linear Regression (OLS)
**Triggers:** "OLS", "linear regression", "ordinary least squares", "slope", "intercept", "fit a linear trend", "linear trend", "R²", "R-squared", "predict", "forecast"
```bash
# Returns: slope, intercept, r_squared, (optional) prediction
python3 /app/toolkit.py linear_regression '{"x": [1929,1930,...,1942], "y": [1.2,1.3,...,2.1]}'
python3 /app/toolkit.py linear_regression '{"x": [0,1,2,3,4,5,6], "y": [...], "predict_x": 7}'
```
See `regression_methods/SKILL.md` for full details on time indexing, polynomial regression, and exponential smoothing.

## Moving Average & Range
**Triggers:** "moving average", "rolling average", "3-month moving average", "range"
```bash
# Simple 3-period trailing MA
python3 /app/toolkit.py moving_average '{"values": [1,2,3,4,5,6], "window": 3}'
# Centered MA
python3 /app/toolkit.py moving_average '{"values": [...], "window": 3, "centered": true}'
# Range (max - min)
python3 /app/toolkit.py range_stat '{"values": [1.2, 3.4, 2.1, 4.5]}'
```

## Common Pitfalls

- **Unit mismatch:** Table says "millions" but question asks "billions" → divide by 1000
- **HP filter λ:** Always use the value specified in the question
- **Theil index:** All values must be positive — zero values cause errors
- **Volatility:** Uses log returns (`ln(rate2/rate1)`), not simple returns
- **Multi-file extraction:** For time series spanning years, you may need to grep across multiple bulletins and combine values before passing to toolkit
