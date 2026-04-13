# Treasury Bulletin Table Extraction

## Table Format

Treasury Bulletin tables look like this:

```
Table 3.—Budget Receipts and Outlays
(In millions of dollars)

| Category                         | Jan  | Feb  | Mar  | Total |
|----------------------------------|------|------|------|-------|
| National defense                 | 1230 | 1245 | 1267 | 3742  |
|   Army                           |  410 |  415 |  422 | 1247  |
|   Navy                           |  420 |  430 |  445 | 1295  |
| Interest on public debt          |  890 |  910 |  880 | 2680  |
| Total outlays                    | 4230 | 4310 | 4390 |12930  |
```

## Step 1 — Find the Table

```bash
# Search for table by name keyword
grep -n "Budget Receipts" /app/corpus/treasury_bulletin_1990_09.txt | head -10

# Read the surrounding section (tables can be 30-80 lines)
sed -n '450,530p' /app/corpus/treasury_bulletin_1990_09.txt
```

**Critical:** Read the FULL table before extracting any value. Tables often continue below visible rows. Scroll past the last data row to confirm you have everything.

## Step 2 — Read the Unit

Look for the unit in:
- The table title line: `(In millions of dollars)`
- A footnote below the table: `1/ In thousands.`
- Column headers if units differ by column

**Common unit patterns:**
- `(In millions of dollars)` → divide by 1000 to get billions
- `(In billions of dollars)` → multiply by 1000 to get millions
- `(Percent)` → values are already percentages
- `(Seasonally adjusted annual rate)` → do NOT sum monthly values; they are annualized rates
- No unit stated → assume millions (most common for expenditure tables)

## Step 3 — Match the Right Row

Row labels are often indented with spaces to show hierarchy:

```
| National defense                 |  <- top-level category
|   Army                           |  <- subcategory (2-space indent)
|     Regular forces               |  <- sub-subcategory (4-space indent)
```

If the question asks for "National defense", use the top-level row, NOT the sum of sub-rows (the table usually provides this already).

If the question asks for a sub-category, use that specific indented row.

## Step 3b — "Total" Row Selection

When the question asks for "total X" (e.g., "total nominal capital", "total receipts"):
- Look for a row explicitly labeled "Total X" or "Total, X" — NOT individual line items
- Balance sheets have hierarchy: individual accounts → subtotals → "Total capital" → "Total capital and liabilities"
- The word "total" in the question means the AGGREGATE row, not an individual item that sounds related
- If you see both "Capital account: 200" and "Total capital: 8,124" — the question asking for "total capital" wants 8,124
- Print the row you selected AND its label: `"SELECTED ROW: 'Total capital' = 8124"` — verify the label matches what the question asks for

## Step 4 — Match the Right Column

Month columns are usually abbreviated: `Jan`, `Feb`, ..., `Dec`.
Fiscal year columns may be labeled `FY 1990` or `1990` or `Total`.

**Fiscal year vs. calendar year:** U.S. federal fiscal year runs October–September. FY1990 = Oct 1989 – Sep 1990. The question will usually specify which one.

## Step 4a — Exact Date/Month Filter

When a question specifies EXACT months (e.g., "last day of June and September", "as of June 30 and September 30"), include ONLY data from those exact months. If the source table also contains December or March figures, exclude them entirely — do NOT include them in your calculation.

Example: "June and September 1990-1992" = exactly 6 data points: Jun-90, Sep-90, Jun-91, Sep-91, Jun-92, Sep-92. Never add Dec-90 or Dec-91 even if they appear in the same table.

## Step 4b — Verify Your Extraction

After identifying row + column, read 3 adjacent rows to confirm context:
```bash
# If your target is line 350, read lines 347-353
sed -n '347,353p' /app/corpus/treasury_bulletin_YYYY_MM.txt
```
Check:
- Is your row label EXACTLY what the question asks for? (not a similar label)
- Is your column header the correct date/period?
- Do adjacent rows make sense relative to your value?

Print: `"VERIFY: value=X from file=Y line=N row='label' col='header'"` before using the value.

## Step 5 — Extract in Python

```python
# After visually identifying the value, hardcode it for verification
# Include the raw text you found as a comment

# From: treasury_bulletin_1990_09.txt
# Table: "Budget Receipts and Outlays"
# Row: "National defense"
# Col: "Mar"
# Unit: millions of dollars
value = 1267  # raw value from table

# Now do any needed conversion or calculation
value_billions = value / 1000  # convert to billions
print(f"National defense outlays, March 1990: ${value_billions:.3f} billion")
```

## Common Pitfalls

**Pitfall 0 — "In thousands of dollars" means MULTIPLY by 1000**
When the table header says `(In thousands of dollars)` and the question asks for "nominal dollars" or just "dollars", you must MULTIPLY each value by 1000. The table value `32,154,441` in thousands = `32,154,441,000` dollars (32 billion). Never divide.

Common tables with this unit: ESF (Exchange Stabilization Fund), some capital movement tables.

**Pitfall 1 — Missing table continuation**
Tables often have a second block labeled "(Continued)" or repeat the header. Grep for the table name to find ALL instances in the file.

**Pitfall 2 — Footnote markers in values**
A value like `1,234 1/` has a footnote marker (`1/`). The actual value is `1234`. Read the footnote to see if it changes the interpretation (e.g., "revised").

**Pitfall 3 — Dash, asterisk, or blank cells**
`—` or `*` means "not applicable" or "less than $500,000". Do NOT treat these as zero.

**Pitfall 4 — Comma-formatted numbers**
`12,345` means 12345, not 12.345. Strip commas before using in Python.

```python
raw_string = "12,345"
value = float(raw_string.replace(",", ""))  # → 12345.0
```

**Pitfall 5 — Negative values**
Deficits or deductions may appear as `(1,234)` or `-1,234`. Both mean negative 1234.

```python
raw_string = "(1,234)"
if raw_string.startswith("(") and raw_string.endswith(")"):
    value = -float(raw_string[1:-1].replace(",", ""))
```

**Pitfall 6 — Revised figures**
Later bulletins sometimes publish revised figures for previous months. If you're looking for the "official" final figure, prefer the most recent bulletin that covers that period.
