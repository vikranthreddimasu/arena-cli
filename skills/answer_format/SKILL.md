# Answer Formatting Rules

## Output File

Always write your final answer to `/app/answer.txt` using Python:
```python
with open('/app/answer.txt', 'w') as f:
    f.write("12.34%\n")
```

## Format by Question Type

### Single numerical value
```
12.34%        # percent, rounded to hundredths
3.456         # billions, rounded to thousandths
42            # integer count
```

### Multi-part answer
Comma-separated, in square brackets, in the order the sub-questions were asked:
```
[12.345, 0.678]
[42, 100.00%]
```

### Percent values
- Write as `12.34%` (not `0.1234`) unless the question specifies otherwise
- **Percent CHANGE** ("percent change", "growth rate"): `|new − old| / old × 100` — denominator is the OLD value
- **Percent DIFFERENCE** ("percent difference", "absolute percent difference"): `|a − b| / ((a+b)/2) × 100` — denominator is the AVERAGE. Use toolkit: `python3 /app/toolkit.py percent_difference '{"a": N, "b": N}'`
- These give DIFFERENT numbers for the same inputs. Example: 528 vs 693 → percent change = 31.25%, percent difference = 27.0%
- **CRITICAL:** The toolkit's CAGR command already returns percent — do NOT multiply by 100 again. But if you compute raw Python formulas like `(end/start)**(1/n) - 1`, the result is a decimal (e.g., `0.076`) — you MUST multiply by 100 before writing (`0.076 → 7.60%`). Never round a decimal to get your percent (e.g., `0.08` is WRONG for 7.60%).

### Comma-separated lists of values
- When listing monetary values (millions, billions), use **thousands separators**: `50,000` not `50000`
- Separate list items with comma-space: `50,000, 52,000, 54,000`
- Use square brackets for multi-part: `[50,000, 52,000, 54,000]`
- Match the formatting style shown in the question — if the question shows `120,000`, use that format

### Format Matching (CRITICAL)
Before writing your answer, re-read the question and identify the expected format:
- Does the question show numbers with commas? → Use `f"{value:,}"` in Python
- Does the question use brackets? → Wrap in `[...]`
- Does the question show decimals? → Match decimal places exactly

Example — if the question expects `[120,000, 135,000]`:
```python
values = [120000, 135000]
formatted = ', '.join(f"{v:,}" for v in values)
with open('/app/answer.txt', 'w') as f:
    f.write(f"[{formatted}]\n")
# Writes: [120,000, 135,000]
```

### Multi-value list extraction (CRITICAL)
When a question asks for a list of values across a date range (e.g., "from 1969 to 1980"):

1. **Count first:** Calculate exactly how many values are needed. "1969 to 1980 inclusive" = 12 values. Write this count down before extracting any data.
2. **Build a labeled table:** Create an explicit year→value mapping in Python. Print each entry:
   ```python
   data = {2001: 50000, 2002: 52000, ...}
   print(f"Count: {len(data)} (expected: 12)")
   for year, val in sorted(data.items()):
       print(f"  {year}: {val}")
   ```
3. **Verify boundaries:** Confirm your first value matches the START year and your last value matches the END year. Off-by-one errors are common.
4. **Cross-check each value:** After building the list, re-read the source table for at least the first, last, and any suspicious values.
5. **Verify count again:** Before writing, confirm `len(values) == expected_count`.

## Rounding Rules

- Round **only** at the final step — carry full precision through calculations
- "Nearest hundredths" → 2 decimal places (e.g., `12.34%`)
- "Nearest thousandths" → 3 decimal places (e.g., `3.456`)
- 1% scoring tolerance — getting the right value matters more than rounding direction

## Units

Match the unit the question asks for:
- "billions of nominal dollars" → express as e.g. `3.456` (not `3,456,000,000`)
- "millions of dollars" → express as e.g. `1234.56`
- If the source table uses millions but the question asks for billions, divide by 1000

## Verification Checklist

Before writing to `/app/answer.txt`:
- [ ] Did I use only values from the corpus (not memorized figures)?
- [ ] Did I match the exact years/months/periods the question specifies?
- [ ] Did I note the table's unit (millions vs billions)?
- [ ] Did I apply the correct formula?
- [ ] Did I round only at the final step?
- [ ] Does my answer format match the question (%, brackets, decimal places)?
