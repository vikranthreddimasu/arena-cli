# Regression & Forecasting Methods

ALWAYS use toolkit functions — never implement from scratch.

## OLS Linear Regression
**Triggers:** "OLS", "ordinary least squares", "linear regression", "slope", "intercept", "fit a linear trend", "fit a line"

```bash
# x = independent variable values (years, time index, etc.)
# y = dependent variable values
python3 /app/toolkit.py linear_regression '{"x": [1929,1930,1931], "y": [1.2,1.3,1.1]}'
# Returns: {"slope": N, "intercept": N, "r_squared": N}

# With prediction for a specific x value:
python3 /app/toolkit.py linear_regression '{"x": [1929,1930,1931], "y": [1.2,1.3,1.1], "predict_x": 2000}'
# Returns: {"slope": N, "intercept": N, "r_squared": N, "prediction": N}
```

### Common patterns:

**"Use year as predictor (numeric, untransformed)"** → pass actual years as x:
```bash
python3 /app/toolkit.py linear_regression '{"x": [1929,1930,...,1942], "y": [...]}'
```

**"Set t=0 in FY 1961"** → pass time index starting at 0:
```bash
python3 /app/toolkit.py linear_regression '{"x": [0,1,2,3,4,5,6], "y": [...]}'  # FY1961-1967
```

**Forecast error** = actual value − predicted value (can be positive or negative)

**R² only**: if the question asks only for R² (goodness of fit), just read the `r_squared` field from the output — do not report slope or intercept.

## Polynomial Regression
**Triggers:** "polynomial regression", "degree 2", "quadratic", "cubic", "degree N polynomial"

```bash
python3 /app/toolkit.py polynomial_regression '{"x": [1,2,3,4,5], "y": [10,12,15,19,24], "degree": 2}'
# Returns: {"coefficients": [c0, c1, c2], "r_squared": N}
# coefficients[0] = constant, coefficients[1] = linear, coefficients[2] = quadratic

# With prediction:
python3 /app/toolkit.py polynomial_regression '{"x": [...], "y": [...], "degree": 3, "predict_x": 2014}'
```

## Single Exponential Smoothing
**Triggers:** "exponential smoothing", "smoothed forecast", "single ES", "alpha value of X"

```bash
python3 /app/toolkit.py exponential_smoothing '{"values": [120,115,118,122], "alpha": 0.4, "forecast_periods": 1}'
# Returns: {"smoothed": [...], "forecast": N}
# "forecast" is the next-period prediction (S_T+1 = S_T since no trend)
```

- Initial value S_1 = y_1 (first observation)
- Each subsequent: S_t = α × y_t + (1-α) × S_{t-1}
- Forecast for next period = last smoothed value

## Moving Averages
**Triggers:** "moving average", "rolling average", "3-month moving average", "centered moving average"

```bash
# Simple n-period moving average (trailing)
python3 /app/toolkit.py moving_average '{"values": [1,2,3,4,5,6], "window": 3}'
# Returns: [2.0, 3.0, 4.0, 5.0]  (4 values for 6 inputs with window 3)

# Centered moving average
python3 /app/toolkit.py moving_average '{"values": [1,2,3,4,5], "window": 3, "centered": true}'
# Returns: [1.5, 2.0, 3.0, 4.0, 4.5]  (one value per input)
```

**Range of moving averages** = max(MA values) - min(MA values):
```bash
# 1. Compute MAs
# 2. Get range:
python3 /app/toolkit.py range_stat '{"values": [MA1, MA2, MA3, ...]}'
```

## Std Dev & Coefficient of Variation

```bash
# Population std dev (default)
python3 /app/toolkit.py std_dev '{"values": [10, 20, 30]}'

# Sample std dev (divide by N-1)
python3 /app/toolkit.py std_dev '{"values": [10, 20, 30], "population": false}'

# Coefficient of variation = (population std / |mean|) × 100
python3 /app/toolkit.py coefficient_of_variation '{"values": [10, 20, 30]}'
# Returns: 40.825 (percent)

# CV of log growth rates (for "expenditure volatility index"):
python3 << 'EOF'
import math, json, subprocess
values = [100, 110, 105, 120, 115]  # raw series
log_rates = [math.log(values[i]/values[i-1]) for i in range(1, len(values))]
result = subprocess.run(['python3', '/app/toolkit.py', 'coefficient_of_variation',
                        json.dumps({"values": log_rates})], capture_output=True, text=True)
print(result.stdout)
EOF
```
