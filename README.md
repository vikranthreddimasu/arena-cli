# Arya

**Arya** (named after [Aryabhata](https://en.wikipedia.org/wiki/Aryabhata)) is a prompt-driven AI agent that achieved the **highest accuracy ever recorded on the OfficeQA benchmark** — 72.0% success rate — in [Sentient Labs Arena](https://www.sentient.xyz/arena) Cohort 0.

Built solo by [Vikranth Reddimasu](https://github.com/vikranthreddimasu).

---

## Results

| Metric | Best Score Run | Highest Accuracy Run |
|--------|---------------|---------------------|
| **Date** | Apr 5, 2026 | Apr 3, 2026 |
| **Harness** | Goose | OpenHands-SDK |
| **Score** | **191.0** | 188.0 |
| **Success rate** | 70.7% | **72.0%** |
| **Cost per run** | $0.01 | $0.07 |
| **Avg time/task** | 186.01s | 144.39s |
| **Model** | Minimax M2.5 | Minimax M2.5 |

- The **191.0 peak score** was achieved with the system prompt alone — no skill files loaded at runtime, no MCP servers.
- The **72.0% success rate** is the highest accuracy ever recorded on the OfficeQA benchmark, surpassing all prior frontier agent results.
- The highest-accuracy run scored lower overall (188.0 vs 191.0) because OpenHands-SDK incurred $0.07 cost vs Goose's $0.01.
- Another team matched the second-best accuracy of 70.7% but scored ~1 point higher due to a 0.3 s/task latency advantage.

---

## The Task

The [Sentient Arena](https://arena.dev) OfficeQA benchmark tests AI agents on quantitative data analysis questions over a corpus of **697 Treasury Bulletin text files** (`treasury_bulletin_YYYY_MM.txt`) spanning decades of U.S. fiscal data.

Each task provides:
- A natural language instruction (e.g., "What is the CAGR of defense spending from FY1961 to FY1967?")
- A Docker environment containing the full corpus as Markdown files with pipe-delimited tables
- Shell and Python access

The agent must search the corpus, extract the right values from the right tables, compute a precise numerical answer, and write it to `/app/answer.txt`.

**Scoring formula** combines three factors:
- **Accuracy** — correctness of the answer (1% tolerance)
- **Cost** — LLM API cost (lower is better; steep penalty for MCP servers)
- **Latency** — time per task (lower is better)

This creates a three-way tradeoff: agents must be correct, cheap, and fast simultaneously.

### Why it's hard

- **697 files**, each 700+ lines — brute-force reading is impossible within time/cost limits
- Tables have **multi-level headers**, footnote markers, continuation sections, and inconsistent formatting
- Data appears in bulletins **1-3 months after** the reporting period (e.g., FY1990 data appears in Oct/Nov 1990 bulletins)
- Fiscal year (Oct-Sep) vs calendar year conventions
- Units vary between tables: millions, billions, thousands, percent
- Chart/figure data exists only in images, not in the text corpus
- Some questions require chaining multiple computations: extract → adjust for inflation → compute regression → format

---

## Approach

Arya is intentionally minimal. The entire agent is a **single 6.3 KB Jinja2 system prompt** (`prompts/system.j2`) that encodes a strict workflow:

```
SEARCH → EXTRACT → WRITE preliminary answer → COMPUTE → STOP
```

No MCP servers. No external tools beyond what the harness provides (shell and Python). No custom agent code. The prompt *is* the agent.

### Architecture

```
┌─────────────────────────────────────────────────┐
│  arena.yaml                                     │
│  ├─ harness: goose / openhands-sdk              │
│  ├─ model: minimax/minimax-m2.5 (via OpenRouter)│
│  └─ prompt_template_path: prompts/system.j2     │
│                                                 │
│  ┌───────────────────────────────────────────┐   │
│  │  system.j2 (the entire agent)             │   │
│  │  ├─ Step 0: Analyze the question          │   │
│  │  ├─ Step 1: Create toolkit.py (heredoc)   │   │
│  │  ├─ Toolkit reference table               │   │
│  │  ├─ Search strategy                       │   │
│  │  ├─ Answer format rules                   │   │
│  │  ├─ Multi-value list protocol             │   │
│  │  └─ 23 operational rules                  │   │
│  └───────────────────────────────────────────┘   │
│                                                 │
│  At runtime (inside Docker container):          │
│  grep → sed → python3 /app/toolkit.py           │
│  └─ writes → /app/answer.txt                    │
└─────────────────────────────────────────────────┘
```

### The system prompt workflow

The prompt in `prompts/system.j2` instructs the agent through a strict sequence:

**Step 0 — Analyze the question.** Before searching, write a scratchpad with:
- GOAL: what specific data values are needed
- PERIOD: time range
- UNIT: expected answer unit (%, millions, etc.)
- EXPECTED_COUNT: how many values needed

**Step 1 — Create the toolkit.** The prompt contains a full Python toolkit as a heredoc that the agent writes to `/app/toolkit.py` on the first tool call. This ensures every computation is done programmatically, never by mental math.

**Search strategy.** The agent uses `grep -rn` to find relevant files, then `sed -n` to read targeted line ranges. It never reads entire files (700+ lines each). Grep results are always piped through `| head -10` to avoid context overflow.

**Write-early rule.** Once any relevant value is extracted, the agent must write a preliminary answer immediately. A wrong answer scores higher than a missing file. This is then refined as more data is found.

**23 operational rules** covering: column verification, unit conversion, fiscal year lag, percent change vs percent difference, HP filter usage, regression conventions, and more.

### Key design decisions

**1. Write-early rule.**
The agent must write a preliminary answer to `/app/answer.txt` within 3-5 tool calls, before any further computation. This eliminated most empty-file failures — a missing answer is an automatic zero. For multi-value tasks, partial lists are written after collecting 3+ values and updated incrementally.

**2. Pre-written formulas.**
The prompt carries copy-paste Python snippets for every computation type encountered:

| Function | Use case |
|----------|----------|
| `percent_change` | Growth rates, "how much did X change" |
| `percent_difference` | Symmetric comparison of two values |
| `cagr` | Compound annual growth rate |
| `arithmetic_mean` | Simple averages |
| `geometric_mean` | Geometric averages |
| `std_dev` | Population/sample standard deviation |
| `coefficient_of_variation` | CV as percentage |
| `linear_regression` | OLS with slope, intercept, R², prediction |
| `polynomial_regression` | Degree-N polynomial fit |
| `exponential_smoothing` | Single ES with forecast |
| `moving_average` | Trailing or centered moving average |
| `range_stat` | Max minus min |
| `hp_filter` | Hodrick-Prescott trend/cycle decomposition |
| `theil_index` | Inequality measurement (GE(1)) |
| `annualized_volatility` | Log-return based volatility |
| `count_local_maxima` | Strict local peaks in a series |
| `count_local_minima` | Strict local troughs in a series |
| `euclidean_norm` | L2 norm of a vector |
| `abs_diff` | Absolute difference |
| `parse_table` | Parse pipe-delimited Markdown tables |

The model copies these rather than inventing formulas, which eliminated mental math errors.

**3. Python-only computation.**
All arithmetic goes through `python3 /app/toolkit.py <command> '<json>'`. The toolkit (`skills/toolkit.py`) includes a comprehensive self-test suite to verify correctness.

**4. Lean prompt — the 6.3 KB sweet spot.**
Input tokens hit ~96% cache hit rate (essentially free), but each extra iteration generates full-price output tokens. More inline guidance → fewer turns → lower cost → higher score. The sweet spot was found through 20+ submissions. Every addition beyond 6.3 KB — formatting rules, inlined skills, harness swaps — caused regression.

**5. No MCP servers.**
The corpus is pre-parsed into grep-searchable text files. A `grep → sed → python3` pipeline is sufficient, and the cost penalty for MCP servers in the scoring formula is steep.

**6. No skill files at runtime.**
Nine skill files were built (see `skills/` directory) as reference documentation, but they were never loaded at runtime for the top-scoring submissions. The system prompt alone was sufficient.

---

## Version Evolution

Three inflection points shaped the final design across 20+ submissions:

### v0.1 → v1.0: Data hygiene
Discovered that early submissions contained **leaked benchmark answers** in skill example files. Cleaned all skill files and replaced examples with fictional values. This was critical — leaked answers could inflate scores but would fail on the server's held-out test set.

### v4.0: Cost economics
**Shorter prompts cost more, not less.** Counter-intuitive finding:
- Input tokens are cached at ~96% hit rate → essentially free
- Each additional iteration generates full-price **output** tokens
- Stripping inline guidance from the prompt reduced input tokens but forced the agent into more turns
- Cost jumped from $12 to $19 with negligible accuracy gain

This led to the strategy of front-loading all guidance into the system prompt.

### v8.0: The sweet spot
Found the **6.3 KB optimal prompt size**. Every modification after this point — formatting rules, inlined skills, harness swaps — caused regression. The final prompt was frozen at v8.0 for the top-scoring submissions.

---

## Failure Analysis

Systematic analysis of 20 tasks across 2 identical runs:

### Failure categories

| Category | Count | Root cause | Fixable? |
|----------|-------|-----------|----------|
| **Chart/figure questions** | 2 | Data exists only in images, not in the text corpus. OCR captures chart titles and axis labels but not plotted data values. | No |
| **Column extraction error** | 4 | Despite explicit `split('\|')` instructions in the prompt, the agent visually estimated column positions rather than splitting programmatically. | Partial |
| **100x unit/scale error** | 2 | % vs ratio confusion — the agent multiplied an already-percentage value by 100 again, or confused "in thousands" with "in millions". | Flaky |
| **Formatting mismatch** | 2 | Trailing newlines, spaces after commas, wrong sign convention. The scoring has tight format expectations. | Sensitive |
| **Non-deterministic** | 5 | Same question yields different answers across runs with identical code. Temperature/sampling variance in M2.5. | No |

### Variance problem

The same v8.0 code produced scores from **150 to 191** — a 41-point spread. 5 of 20 tasks flipped between pass and fail on identical code. This makes systematic improvement extremely difficult: you can't tell if a change helped or if you just got a lucky roll.

### What worked

- **Write-early rule** — eliminated empty-file failures (automatic zeros)
- **Python-only computation** — eliminated mental math errors
- **Pre-written formulas** — model copies rather than invents, reducing hallucinated math
- **`split('|')` column indexing** — explicit instructions for programmatic column extraction
- **Lean prompt** — fewer iterations, lower cost, higher score

### What didn't work

- **Formatting constraints** — more tokens for no scoring benefit
- **Inlining skill content** — bloated the prompt, increased cost, caused regression
- **Removing the formula toolkit** — model still needed explicit formula references even without the toolkit file

### Future directions

- Custom MCP server for Treasury Bulletin structure-aware retrieval (understanding table schemas, not just grep)
- Multi-pass verification on high-uncertainty tasks
- Systematic A/B testing with sufficient submissions to overcome variance
- Chart question workarounds via equivalent text-table data elsewhere in the corpus

---

## Toolkit

The statistical toolkit (`skills/toolkit.py`) is a self-contained Python script with 20 functions and a comprehensive self-test suite.

### Usage

```bash
# Direct invocation
python3 toolkit.py percent_change '{"old": 100, "new": 150}'
# → 50.0

python3 toolkit.py cagr '{"start_val": 100, "end_val": 200, "periods": 10}'
# → 7.177...

python3 toolkit.py hp_filter '{"y": [1, 2, 3, 4, 5], "lamb": 100}'
# → {"trend": [1.0, 2.0, 3.0, 4.0, 5.0], "cycle": [0.0, 0.0, 0.0, 0.0, 0.0]}

python3 toolkit.py linear_regression '{"x": [0,1,2,3], "y": [10,12,15,19], "predict_x": 4}'
# → {"slope": 3.0, "intercept": 9.5, "r_squared": 0.986, "prediction": 21.5}

# Run all self-tests
python3 toolkit.py --selftest
```

### Self-test coverage

The toolkit includes tests for:
- Scalar functions (percent_change, arithmetic_mean, geometric_mean, CAGR, Theil index, euclidean_norm, local maxima/minima, abs_diff, annualized volatility)
- HP filter (linear data, lambda=0, analytical solution, reconstruction check, large lambda convergence to OLS)
- Table parser (2-row Markdown table with headers)

### Design notes

- **HP filter** uses Gaussian elimination with partial pivoting to solve the (I + λK'K) system. Custom implementations often get boundary conditions wrong — this was a common failure mode before centralizing it in the toolkit.
- **CAGR** returns percent directly (e.g., 7.177, not 0.07177). The prompt explicitly warns: "do NOT multiply by 100 again."
- **`percent_change` vs `percent_difference`** — these are different formulas that give different results for the same inputs. The prompt has explicit rules distinguishing them. This was one of the most common failure modes.

---

## Skill Files

Nine skill files in `skills/` provide reference documentation for different aspects of the task. These were built during development but **never loaded at runtime** for the top-scoring submissions.

| Skill | Purpose |
|-------|---------|
| `toolkit.py` | Statistical computation toolkit (20 functions + self-tests) |
| `answer_format/SKILL.md` | Output formatting: single values, multi-part, percent, comma-separated lists, rounding |
| `chart_analysis/SKILL.md` | Reconstructing chart data from corpus, counting peaks across multiple series |
| `computational_methods/SKILL.md` | Complete reference for all toolkit commands with triggers and examples |
| `corpus_search/SKILL.md` | How to search 697 Treasury Bulletin files: timing, keywords, fiscal year conventions |
| `cpi_adjustment/SKILL.md` | Inflation adjustment using BLS CPI-U annual averages (1913-2024 lookup table) |
| `regression_methods/SKILL.md` | OLS, polynomial regression, exponential smoothing, moving averages, std dev, CV |
| `table_extraction/SKILL.md` | Parsing pipe-delimited tables: units, row matching, "total" row selection, common pitfalls |


The skills remain valuable as development documentation and for understanding the problem domain.

---

## Agent Configuration

### arena.yaml

```yaml
name: "arya"
version: "0.1.0"
competition: "grounded-reasoning"

agent:
  type: "harness"
  harness_name: "openhands-sdk"              # also tested with "goose"
  model: "openrouter/minimax/minimax-m2.5:free"
  prompt_template_path: "prompts/system.j2"
  skills_dir: "skills/"
  config:
    reasoning_effort: "high"
  env:
    OPENROUTER_API_KEY: "${oc.env:OPENROUTER_API_KEY,''}"

environment:
  memory: "4G"
  timeout_per_task: 600                      # seconds (max allowed)
```

### Harness comparison

Both Goose and OpenHands-SDK were tested. The tradeoff:

| | Goose | OpenHands-SDK |
|---|-------|--------------|
| **Best score** | 191.0 | 188.0 |
| **Best accuracy** | 70.7% | 72.0% |
| **Cost** | $0.01 | $0.07 |
| **Speed** | 186.01 s/task | 144.39 s/task |

Goose scored higher overall due to lower cost despite slightly lower accuracy. OpenHands-SDK was faster and more accurate but 7x more expensive per run.

### Model choice

**Minimax M2.5** was used for all server submissions via OpenRouter (free tier). Locally, **Minimax M2.7** was used for trace analysis — it has 2x max output tokens, slightly more context, and better throughput, producing higher-quality traces to analyze failure patterns.

Note: The model field in `arena.yaml` had no server-side effect during Cohort 0 — the server always ran M2.5 regardless of configuration.

---

## Repository Structure

```
.
├── arena.yaml                          # Agent configuration (harness, model, prompt path)
├── prompts/
│   └── system.j2                       # The system prompt — this IS the agent (6.3 KB)
├── skills/
│   ├── toolkit.py                      # Statistical toolkit (20 functions + self-tests)
│   ├── answer_format/SKILL.md          # Answer formatting rules
│   ├── chart_analysis/SKILL.md         # Chart/visual data reconstruction
│   ├── computational_methods/SKILL.md  # Toolkit command reference
│   ├── corpus_search/SKILL.md          # Treasury Bulletin search guide
│   ├── cpi_adjustment/SKILL.md         # BLS CPI-U inflation adjustment (1913-2024)
│   ├── regression_methods/SKILL.md     # Regression, smoothing, moving averages
│   └── table_extraction/SKILL.md       # Pipe-delimited table parsing
├── install.sh                          # Arena CLI installer (uses uv)
├── pyproject.toml                      # Python project metadata
├── Vikranth Reddimasu.pdf              # Cohort 0 final report (detailed writeup)
├── version.json                        # CLI version info
├── .gitignore                          # Excludes .whl, .env, runs, samples
└── .python-version                     # Python 3.11
```

Pre-built `.whl` wheels (`arena_cli`, `arena_core`, `arena_sdk`, `harbor`) are excluded from the repo via `.gitignore`. The CLI source is maintained at [sentient-agi/arena](https://github.com/sentient-agi/arena).

---

## Setup

### Prerequisites

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (for local testing)
- An [OpenRouter](https://openrouter.ai/) API key

### Installation

```bash
# Install the Arena CLI
./install.sh
export PATH="$HOME/.arena/bin:$PATH"

# Add to your shell profile
echo 'export PATH="$HOME/.arena/bin:$PATH"' >> ~/.zshrc

# Authenticate with Arena
arena auth login

# Validate setup
arena doctor
```

### Set your API key

```bash
export OPENROUTER_API_KEY="sk-or-..."
```

### Local testing

```bash
# Validate arena.yaml (no Docker needed)
arena test --dry-run

# Run 1 sample task (requires Docker)
arena test --smoke

# Run N tasks
arena test --n 5

# Run all downloaded samples
arena test --all

# Filter by task pattern
arena test --filter "officeqa-*"

# Download latest sample tasks
arena pull

# Inspect the latest run trajectory
arena view
```

### Submission

```bash
# Submit for server-side evaluation
arena submit

# Check submission status
arena status <submission-id>

# Stream live results
arena results <submission-id>

# View submission history
arena history

# Compare two submissions side-by-side
arena compare <id-1> <id-2>

# Check your ranking
arena leaderboard

# Check remaining quota
arena quota
```

### Run output

Results are saved to `.arena/runs/<run-id>/` containing:
- `trajectory.json` — ATIF trajectory (full agent action log)
- `verifier-result.json` — pass/fail per task with scores
- Agent and environment logs

---

## Execution Flow

When `arena test` runs:

1. CLI reads `arena.yaml` → validates configuration
2. Harbor runtime loads sample tasks from `.arena/samples/`
3. For each task:
   - Docker container is built from the task's `task.toml`
   - The corpus (697 Treasury Bulletin files) is mounted at `/app/corpus/`
   - The harness agent (Goose/OpenHands-SDK) is instantiated with `system.j2` as the system prompt
   - The `{{ instruction }}` placeholder in the prompt is replaced with the task question
4. The agent executes:
   - Writes `toolkit.py` to `/app/toolkit.py` (from the heredoc in the prompt)
   - Searches corpus with `grep -rn` → reads targeted lines with `sed -n`
   - Extracts values, writes preliminary answer to `/app/answer.txt`
   - Computes final answer using `python3 /app/toolkit.py`
   - Overwrites `/app/answer.txt` with the refined answer
5. Verifier runs tests against the answer; results + trajectory written to `.arena/runs/<run-id>/`

---

## Lessons Learned

### Simplicity wins
M2.5 performs best with concise, direct instructions. The 6.3 KB sweet spot was found through 20+ submissions. Every content addition — formatting rules, inlined skills — caused regression. The agent doesn't need to be told everything, just the right things in the right order.

### Variance dominates
The same v8.0 code produced scores from 150 to 191 — a **41-point spread**. 5 of 20 tasks flipped between pass and fail on identical code. This makes systematic improvement extremely difficult: you can't distinguish signal from noise without many submissions.

### Cost-accuracy tradeoff is counterintuitive
Input caching makes longer prompts essentially free (~96% cache hit rate). More inline guidance → fewer turns → fewer output tokens → lower cost → higher score. The cheapest agent is not the one with the shortest prompt — it's the one that solves the task in the fewest iterations.

### The model copies, it doesn't invent
Pre-written formulas that the model can copy verbatim outperform expecting the model to derive formulas from descriptions. `percent_change` vs `percent_difference` was a persistent failure mode until explicit formulas were added. The model would consistently confuse them when given only descriptions.

### Write early, write often
A wrong answer scores higher than no answer. Requiring a preliminary answer within 3-5 tool calls eliminated the most devastating failure mode: empty `answer.txt` files that score automatic zeros.

---

## About the Competition

[Sentient Labs Arena](https://www.sentient.xyz/arena) is a competition platform for evaluating AI coding/analysis agents. Cohort 0 ran in March-April 2026 with the OfficeQA benchmark — a dataset of quantitative questions over U.S. Treasury Bulletin data originally created by [Databricks](https://github.com/databricks/officeqa).

The Arena provides:
- Pre-built harness agents: OpenCode, Codex, Goose, OpenHands-SDK
- Docker-based task environments
- Server-side evaluation with scoring that balances accuracy, cost, and latency
- A leaderboard and submission tracking


---

## License

This project was built for the Sentient Labs Arena competition (Cohort 0). The Arena CLI and harness agents are provided by [Sentient AGI](https://github.com/sentient-agi/arena).
