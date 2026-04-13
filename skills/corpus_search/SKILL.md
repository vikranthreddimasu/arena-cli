# Treasury Bulletin Corpus Search Guide

## Corpus Structure

- Location: `/app/corpus/`
- 697 files: `treasury_bulletin_YYYY_MM.txt`
- Index of all files: `/app/corpus/index.txt`
- Format: Markdown text with tables (pipe-delimited `|` rows)

## Finding the Right File(s)

Data is often reported in bulletins **after** the period it covers:
- Monthly data for January 1953 → likely in `treasury_bulletin_1953_02.txt` or `_03.txt`
- Annual totals for 1940 → may appear in 1941 bulletins
- Historical series → often reprinted in later bulletins

```bash
# List files for a year range
ls /app/corpus/treasury_bulletin_194*.txt
ls /app/corpus/treasury_bulletin_195*.txt

# Read the full index
cat /app/corpus/index.txt
```

## Searching for Keywords

```bash
# Find which files mention a topic
grep -rl "national defense" /app/corpus/ | head -10

# Search with line numbers in a specific file
grep -n "expenditure" /app/corpus/treasury_bulletin_1953_06.txt | head -10

# Case-insensitive search across all files
grep -ril "exchange stabilization" /app/corpus/ | head -10

# Show context around a match (5 lines before and after)
grep -n -A 5 -B 5 "defense" /app/corpus/treasury_bulletin_1953_06.txt | head -30
```

## Reading Tables

Treasury Bulletin tables look like this:
```
| Category                    | Jan  | Feb  | Mar  | Total |
|-----------------------------|------|------|------|-------|
| National defense            | 1.23 | 1.45 | 1.67 | 4.35  |
| Interest on public debt     | 0.89 | 0.91 | 0.88 | 2.68  |
```

Tips:
- Units are usually stated in the table title or a footnote (e.g., "In millions of dollars")
- Row labels may be indented with spaces for subcategories
- "Total" rows may be labeled "Grand total", "All items", or similar
- Some tables continue across multiple sections — scroll down past the header

## Common Metric Names to Search For

| Topic | Search terms |
|-------|-------------|
| Defense spending | `national defense`, `military`, `defense activities` |
| Intergovernmental | `intergovernmental`, `grants`, `transfers` |
| ESF Balance Sheet | `exchange stabilization`, `ESF`, `stabilization fund` |
| Public debt | `public debt`, `outstanding debt`, `securities` |
| Tax receipts | `internal revenue`, `receipts`, `customs` |

## Cost-Efficient Reading

**Never read entire files — they are 700+ lines.** Always grep first, then read targeted lines:

```bash
# Step 1: find the line number
grep -n "national defense" /app/corpus/treasury_bulletin_1990_09.txt | head -10

# Step 2: read only lines 200-250 (adjust based on grep output)
sed -n '200,250p' /app/corpus/treasury_bulletin_1990_09.txt
```

## When Data Spans Multiple Bulletins

If the question asks for all 12 months of a calendar year individually:
1. Annual summary tables (usually in Dec or Jan bulletins) often list all 12 months
2. If not found in one file, check 2–3 bulletins from that year
3. Monthly data accumulates — an annual total = sum of all monthly values for that year

## Fiscal Year Data

The U.S. fiscal year ends September 30. For fiscal year data:
- Check September or October bulletins for annual totals
- Table FFO-1 (Summary of Fiscal Operations) often has multi-year fiscal data
- "Fiscal 1990" means Oct 1989 – Sep 1990

## Multi-Year Lookups

For questions spanning many years (e.g., "1961 to 1970"):
1. First check if a **single bulletin** has a summary table covering the full range
2. Tables like FD-1, OFS-1, or MY-1 often have multi-year historical data
3. Only read individual bulletins if no summary table exists
