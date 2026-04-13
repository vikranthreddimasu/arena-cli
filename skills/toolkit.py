#!/usr/bin/env python3
"""
Treasury Bulletin Statistical Toolkit
Usage: python3 toolkit.py <command> '<json_args>'
       python3 toolkit.py --selftest
"""
import sys
import json
import math


def percent_change(args):
    """Absolute percent change: |new - old| / old * 100"""
    old = float(args['old'])
    new = float(args['new'])
    absolute = args.get('absolute', True)
    result = (new - old) / old * 100
    return abs(result) if absolute else result


def arithmetic_mean(args):
    """Mean of a list of values."""
    values = [float(v) for v in args['values']]
    return sum(values) / len(values)


def geometric_mean(args):
    """Geometric mean: exp(mean(ln(x_i))). All values must be positive."""
    values = [float(v) for v in args['values']]
    log_sum = sum(math.log(v) for v in values)
    return math.exp(log_sum / len(values))


def cagr(args):
    """Compound annual growth rate: (end/start)^(1/n) - 1, returned as %."""
    start = float(args['start_val'])
    end = float(args['end_val'])
    periods = float(args['periods'])
    return ((end / start) ** (1.0 / periods) - 1) * 100


def theil_index(args):
    """Theil T index (GE(1)): (1/n) * sum(xi/mu * ln(xi/mu)). All values must be positive."""
    values = [float(v) for v in args['values']]
    n = len(values)
    mu = sum(values) / n
    return sum((v / mu) * math.log(v / mu) for v in values) / n


def hp_filter(args):
    """
    Hodrick-Prescott filter.
    Solves (I + lamb * K'K) * trend = y where K is the second-difference matrix.
    Returns {"trend": [...], "cycle": [...]}.
    """
    y = [float(v) for v in args['y']]
    lamb = float(args.get('lamb', 100))
    n = len(y)

    if n < 3:
        return {'trend': y[:], 'cycle': [0.0] * n}

    # Build K'K where K is (n-2) x n second-difference matrix
    # K[k] has values [1, -2, 1] at columns [k, k+1, k+2]
    H = [[0.0] * n for _ in range(n)]
    for k in range(n - 2):
        idx = [k, k + 1, k + 2]
        val = [1.0, -2.0, 1.0]
        for a in range(3):
            for b in range(3):
                H[idx[a]][idx[b]] += lamb * val[a] * val[b]
    for i in range(n):
        H[i][i] += 1.0

    # Solve H * tau = y via Gaussian elimination with partial pivoting
    A = [H[i][:] + [y[i]] for i in range(n)]

    for col in range(n):
        # Partial pivoting
        max_row = col
        max_val = abs(A[col][col])
        for row in range(col + 1, n):
            if abs(A[row][col]) > max_val:
                max_val = abs(A[row][col])
                max_row = row
        if max_row != col:
            A[col], A[max_row] = A[max_row], A[col]

        pivot = A[col][col]
        if abs(pivot) < 1e-15:
            continue

        for row in range(col + 1, n):
            factor = A[row][col] / pivot
            for j in range(col, n + 1):
                A[row][j] -= factor * A[col][j]

    # Back substitution
    tau = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = A[i][n]
        for j in range(i + 1, n):
            s -= A[i][j] * tau[j]
        tau[i] = s / A[i][i]

    cycle = [y[i] - tau[i] for i in range(n)]
    return {'trend': tau, 'cycle': cycle}


def euclidean_norm(args):
    """L2 norm: sqrt(sum(xi^2))"""
    vector = [float(v) for v in args['vector']]
    return math.sqrt(sum(v ** 2 for v in vector))


def annualized_volatility(args):
    """
    Annualized realized volatility from a rate series.
    Computes log returns, realized variance (mean of squared returns),
    then annualizes: sqrt(RV * periods_per_year) * 100.
    """
    rates = [float(v) for v in args['rates']]
    periods_per_year = float(args.get('periods_per_year', 52))

    if len(rates) < 2:
        return 0.0

    log_returns = [math.log(rates[i + 1] / rates[i]) for i in range(len(rates) - 1)]
    n = len(log_returns)

    realized_var = sum(r ** 2 for r in log_returns) / n
    annualized_var = realized_var * periods_per_year
    return math.sqrt(annualized_var) * 100


def count_local_maxima(args):
    """Count strict local maxima: series[i-1] < series[i] > series[i+1]."""
    series = [float(v) for v in args['series']]
    count = 0
    for i in range(1, len(series) - 1):
        if series[i] > series[i - 1] and series[i] > series[i + 1]:
            count += 1
    return count


def count_local_minima(args):
    """Count strict local minima: series[i-1] > series[i] < series[i+1]."""
    series = [float(v) for v in args['series']]
    count = 0
    for i in range(1, len(series) - 1):
        if series[i] < series[i - 1] and series[i] < series[i + 1]:
            count += 1
    return count


def abs_diff(args):
    """Absolute difference: |a - b|"""
    return abs(float(args['a']) - float(args['b']))


def parse_table(args):
    """Parse pipe-delimited Markdown table into list of dicts."""
    text = args['text']
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]

    data_lines = []
    for line in lines:
        # Skip separator rows (only |, -, :, spaces)
        cleaned = line.replace('|', '').replace('-', '').replace(' ', '').replace(':', '')
        if not cleaned:
            continue
        data_lines.append(line)

    if len(data_lines) < 2:
        return []

    header = [c.strip() for c in data_lines[0].split('|') if c.strip()]
    result = []
    for line in data_lines[1:]:
        cells = [c.strip() for c in line.split('|') if c.strip()]
        if len(cells) >= len(header):
            result.append(dict(zip(header, cells[:len(header)])))

    return result


COMMANDS = {
    'percent_change': percent_change,
    'arithmetic_mean': arithmetic_mean,
    'geometric_mean': geometric_mean,
    'cagr': cagr,
    'theil_index': theil_index,
    'hp_filter': hp_filter,
    'euclidean_norm': euclidean_norm,
    'annualized_volatility': annualized_volatility,
    'count_local_maxima': count_local_maxima,
    'count_local_minima': count_local_minima,
    'abs_diff': abs_diff,
    'parse_table': parse_table,
}


def _check(name, cmd, args, expected, tol=0.001):
    """Run one test. Returns (passed: bool, message: str)."""
    try:
        result = COMMANDS[cmd](args)
        if isinstance(expected, int):
            ok = result == expected
        else:
            ok = abs(float(result) - expected) <= tol
        status = "PASS" if ok else "FAIL"
        return ok, f"  {status}: {name}\n         expected={expected}, got={result}"
    except Exception as e:
        return False, f"  FAIL: {name}\n         ERROR: {e}"


def selftest():
    """Run sanity checks on all functions with known expected outputs."""
    passed = 0
    failed = 0

    print("=" * 64)
    print("  TOOLKIT SELF-TEST")
    print("=" * 64)

    # --- Scalar function tests ---
    scalar_tests = [
        ("percent_change: 100 → 150", 'percent_change',
         {'old': 100, 'new': 150}, 50.0),
        ("percent_change: 150 → 100 (signed)", 'percent_change',
         {'old': 150, 'new': 100, 'absolute': False}, -33.333),
        ("arithmetic_mean: [1,2,3,4,5]", 'arithmetic_mean',
         {'values': [1, 2, 3, 4, 5]}, 3.0),
        ("geometric_mean: [2, 8]", 'geometric_mean',
         {'values': [2, 8]}, 4.0),
        ("geometric_mean: [1, 3, 9, 27]", 'geometric_mean',
         {'values': [1, 3, 9, 27]}, 5.196),
        ("cagr: 100 → 200 in 10 periods", 'cagr',
         {'start_val': 100, 'end_val': 200, 'periods': 10}, 7.177),
        ("theil_index: equal values [5,5,5]", 'theil_index',
         {'values': [5, 5, 5]}, 0.0),
        ("theil_index: [1, 2, 3]", 'theil_index',
         {'values': [1, 2, 3]}, 0.0872),
        ("euclidean_norm: [3, 4]", 'euclidean_norm',
         {'vector': [3, 4]}, 5.0),
        ("euclidean_norm: [1, 2, 3]", 'euclidean_norm',
         {'vector': [1, 2, 3]}, 3.7417),
        ("count_local_maxima: [1,3,2,4,1]", 'count_local_maxima',
         {'series': [1, 3, 2, 4, 1]}, 2),
        ("count_local_maxima: monotone [1,2,3,4,5]", 'count_local_maxima',
         {'series': [1, 2, 3, 4, 5]}, 0),
        ("count_local_minima: [3,1,4,2,5]", 'count_local_minima',
         {'series': [3, 1, 4, 2, 5]}, 2),
        ("abs_diff: |10 - 7|", 'abs_diff',
         {'a': 10, 'b': 7}, 3.0),
        ("annualized_vol: [100,105,102] weekly", 'annualized_volatility',
         {'rates': [100, 105, 102], 'periods_per_year': 52}, 28.94, 0.1),
    ]

    print("\n  Scalar functions:")
    for item in scalar_tests:
        name, cmd, args, expected = item[0], item[1], item[2], item[3]
        tol = item[4] if len(item) > 4 else 0.01
        ok, msg = _check(name, cmd, args, expected, tol)
        print(msg)
        if ok:
            passed += 1
        else:
            failed += 1

    # --- HP filter tests ---
    print("\n  HP filter:")

    # Test 1: linear data, trend = data
    hp1 = hp_filter({'y': [1, 2, 3, 4, 5], 'lamb': 100})
    hp1_ok = all(abs(hp1['trend'][i] - (i + 1)) < 0.01 for i in range(5))
    print(f"  {'PASS' if hp1_ok else 'FAIL'}: linear [1,2,3,4,5] lambda=100 -> trend = data")
    print(f"         trend = {[round(v, 4) for v in hp1['trend']]}")
    passed += hp1_ok
    failed += not hp1_ok

    # Test 2: lambda=0, trend = data (no smoothing)
    hp2 = hp_filter({'y': [1, 5, 2, 8, 3], 'lamb': 0})
    hp2_ok = all(abs(hp2['trend'][i] - [1, 5, 2, 8, 3][i]) < 0.001 for i in range(5))
    print(f"  {'PASS' if hp2_ok else 'FAIL'}: lambda=0 -> trend = data (no smoothing)")
    print(f"         trend = {[round(v, 4) for v in hp2['trend']]}")
    passed += hp2_ok
    failed += not hp2_ok

    # Test 3: analytical solution y=[1,5,1], lambda=1 -> trend=[15/7, 19/7, 15/7]
    hp3 = hp_filter({'y': [1, 5, 1], 'lamb': 1})
    exp3 = [15.0 / 7, 19.0 / 7, 15.0 / 7]
    hp3_ok = all(abs(hp3['trend'][i] - exp3[i]) < 0.001 for i in range(3))
    print(f"  {'PASS' if hp3_ok else 'FAIL'}: [1,5,1] lambda=1 -> [{15 / 7:.4f}, {19 / 7:.4f}, {15 / 7:.4f}]")
    print(f"         trend = {[round(v, 4) for v in hp3['trend']]}")
    passed += hp3_ok
    failed += not hp3_ok

    # Test 4: trend + cycle = y (reconstruction check)
    y4 = [10, 20, 15, 25, 12, 30, 8]
    hp4 = hp_filter({'y': y4, 'lamb': 100})
    recon = [hp4['trend'][i] + hp4['cycle'][i] for i in range(len(y4))]
    hp4_ok = all(abs(recon[i] - y4[i]) < 1e-9 for i in range(len(y4)))
    print(f"  {'PASS' if hp4_ok else 'FAIL'}: trend + cycle = original data (reconstruction)")
    print(f"         trend = {[round(v, 2) for v in hp4['trend']]}")
    passed += hp4_ok
    failed += not hp4_ok

    # Test 5: large lambda -> trend approaches linear fit
    y5 = [1, 3, 2, 4, 5]
    hp5 = hp_filter({'y': y5, 'lamb': 1e8})
    # OLS fit: y = 1.2 + 0.9*x -> [1.2, 2.1, 3.0, 3.9, 4.8]
    ols = [1.2, 2.1, 3.0, 3.9, 4.8]
    hp5_ok = all(abs(hp5['trend'][i] - ols[i]) < 0.05 for i in range(5))
    print(f"  {'PASS' if hp5_ok else 'FAIL'}: large lambda -> trend ~ OLS linear fit")
    print(f"         trend = {[round(v, 4) for v in hp5['trend']]}")
    print(f"         OLS   = {ols}")
    passed += hp5_ok
    failed += not hp5_ok

    # --- Parse table test ---
    print("\n  Parse table:")
    table_text = "| Year | GDP | Rate |\n|---|---|---|\n| 1960 | 12.3 | 5.1 |\n| 1961 | 13.7 | 4.9 |"
    pt = parse_table({'text': table_text})
    pt_ok = (len(pt) == 2
             and pt[0].get('Year') == '1960'
             and pt[0].get('GDP') == '12.3'
             and pt[1].get('Rate') == '4.9')
    print(f"  {'PASS' if pt_ok else 'FAIL'}: 2-row table with Year/GDP/Rate")
    print(f"         result = {pt}")
    passed += pt_ok
    failed += not pt_ok

    # --- Summary ---
    total = passed + failed
    print()
    print("=" * 64)
    print(f"  RESULTS: {passed}/{total} passed, {failed} failed")
    print("=" * 64)

    return failed == 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 toolkit.py <command> '<json_args>'")
        print("       python3 toolkit.py --selftest")
        print(f"\nAvailable commands: {', '.join(sorted(COMMANDS.keys()))}")
        sys.exit(1)

    if sys.argv[1] == '--selftest':
        success = selftest()
        sys.exit(0 if success else 1)

    cmd = sys.argv[1]
    if cmd not in COMMANDS:
        print(f"Error: unknown command '{cmd}'", file=sys.stderr)
        print(f"Available: {', '.join(sorted(COMMANDS.keys()))}", file=sys.stderr)
        sys.exit(1)

    try:
        args = json.loads(sys.argv[2])
    except (IndexError, json.JSONDecodeError) as e:
        print(f"Error: invalid JSON argument: {e}", file=sys.stderr)
        print(f"Usage: python3 toolkit.py {cmd} '<json>'", file=sys.stderr)
        sys.exit(1)

    result = COMMANDS[cmd](args)
    if isinstance(result, (dict, list)):
        print(json.dumps(result))
    else:
        print(result)
