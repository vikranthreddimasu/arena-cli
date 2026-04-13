# Chart and Visual Analysis

## When to use

Keywords: "local maxima", "local minima", "peaks", "troughs", "how many times does the line", "highest point", "lowest point", "inflection", "crossings".

## Step 1: Find the chart data

**Try the direct approach first** — search for a data table near the chart exhibit:
```bash
grep -n "Exhibit\|Chart\|Figure" /app/corpus/treasury_bulletin_YYYY_MM.txt | head -10
# Then read 70 lines around the match to find the backing table
sed -n 'N,N+70p' /app/corpus/treasury_bulletin_YYYY_MM.txt
```

**IMPORTANT: Chart data may NOT exist as a table in the text file.** The OCR only captures chart titles and axis labels, not the plotted data values. If you find only a title and axis labels (e.g., "Percent 20 15 10 5 0" and "1900 1910 1920..."), the data is NOT there.

## Step 1b: Inventory ALL plots on the page

Before reconstructing data, COUNT how many separate line plots exist on the target page:
1. Read 150+ lines around the page/exhibit to find ALL chart titles, exhibit labels, or series references
2. A single exhibit may contain MULTIPLE line plots (e.g., "Private Saving" and "Total Saving" on one chart)
3. Write down: "Found N separate data series: [series1, series2, ...]"
4. You must reconstruct data for EVERY series — do not stop after finding the first one
5. Annual data spanning 30+ years typically has 8-15 local maxima per series
6. **Write a preliminary answer after reconstructing the FIRST series.** Update it as you add more series. Never finish chart analysis without a written answer

## Step 2: Reconstruct data from the corpus

**Chart data is NEVER directly available as plotted values.** The OCR captures only titles and axis labels. You MUST find the underlying numerical data elsewhere in the corpus.

### Strategy A: Search the same bulletin for data tables
```bash
grep -n "Table\|SUMMARY\|STATEMENT" /app/corpus/treasury_bulletin_YYYY_MM.txt | head -10
```

### Strategy B: Search the FULL corpus for the metric name
```bash
grep -rn "gross saving" /app/corpus/ | head -10
grep -rn "saving ratio" /app/corpus/ | head -10
```

### Strategy C: Assemble year-by-year from multiple bulletins
If the chart spans many years (e.g., 1900-1990), the data may be spread across bulletins:
```bash
grep -rl "metric name" /app/corpus/ | sort | head -10
```

### Where to look
- Summary tables in the same bulletin (different section from the chart)
- Tables in bulletins from adjacent years
- Annual summary tables that list year-by-year values (e.g., FD-1, OFS-1)
- Statistical appendix tables at the end of bulletins
- **Multiple charts on one page = multiple data series.** You MUST find data for ALL series and count peaks across ALL of them, then sum

## Step 3: Extract and compute

Once you have the data as a series, use the toolkit:

```bash
# Count local maxima
python3 /app/toolkit.py count_local_maxima '{"series": [12.3, 13.7, 11.2, 14.0, 13.1]}'

# Count local minima
python3 /app/toolkit.py count_local_minima '{"series": [12.3, 13.7, 11.2, 14.0, 13.1]}'
```

## Step 4: Multiple series — SUM across all

If the question asks about "the line plots on page X":
1. Count peaks for EACH series separately using the toolkit
2. **SUM** the results across all series — the answer is the total, not per-series
3. Print: "Series A: N maxima, Series B: M maxima, ..., TOTAL: N+M+..."
4. If total seems surprisingly low (< 10 for multi-decade data), re-check data completeness

## Edge cases

- **Strict inequality**: `series[i-1] < series[i] > series[i+1]` (use `>`, not `>=`)
- **Boundary points**: First and last values are NEVER maxima/minima
- **Plateau**: `[3, 5, 5, 5, 3]` → 0 local maxima (flat top doesn't satisfy strict `>`)
- **Missing data**: Split series at gaps, analyze each segment separately
- **Don't count charts** — count peaks WITHIN the data series

## Common mistakes

- Counting the number of line series instead of peaks within data
- Estimating by eye instead of running the algorithm
- Including boundary points
- Using `>=` instead of strict `>`
