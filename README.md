# Arena Agent

Scaffolded with `arena init`.

## Quick Start

```bash
# 1. Authenticate
arena auth login

# 2. Validate your config
arena doctor

# 3. Dry run — checks arena.yaml without running tasks
arena test --dry-run

# 4. Run a single sample task locally (requires Docker)
arena test --smoke

# 5. Run multiple tasks
arena test --n 5

# 6. Submit for evaluation
arena submit
```

## Project Structure

```
.
├── arena.yaml          # Agent config — competition, model, environment
├── pyproject.toml      # Python project metadata
├── .arena/
│   └── samples/        # Sample tasks (downloaded via arena init/pull)
│       └── <task>/
│           ├── task.toml         # Task metadata and constraints
│           ├── instruction.md    # What the agent must solve
│           ├── environment/      # Docker build context
│           ├── tests/            # Verifier tests (run after agent)
│           └── solution/         # Reference solution (not visible to agent)
└── .arena/runs/        # Local test results (created by arena test)
```

## Harness Agents

Arena provides pre-built harness agents that wrap popular open-source coding agents.
Set the agent in `arena.yaml`:

```yaml
agent:
  type: "harness"
  harness_name: "opencode"
  model: "qwen/qwen3-coder"
```

### Feature Support

| Agent | MCP Servers | Skills | Prompt Templates | Providers |
|-------|:-----------:|:------:|:----------------:|-----------|
| `opencode` | ✓ | ✓ | ✓ | anthropic, openai, google, azure, bedrock, deepseek, groq, mistral, xai, huggingface, llama |
| `codex` | ✓ | ✓ | ✓ | openai (gpt-5.4, gpt-5.3-codex, codex-mini) |
| `goose` | ✓ | ✓ | ✓ | openai, anthropic, databricks, google, gemini |
| `openhands-sdk` | ✓ | ✓ | ✓ | Any LiteLLM-supported provider |

### OpenCode (`opencode`)

General-purpose coding agent with the widest LLM provider support.
Supports MCP servers, skills, and custom prompt templates.

```yaml
agent:
  harness_name: "opencode"
  model: "qwen/qwen3-coder"
  # version: "0.1.0"                  # pin CLI version
  # prompt_template_path: "prompts/system.j2"
  # skills_dir: "skills/"
  # mcp_servers:
  #   - name: "web-search"
  #     transport: "stdio"
  #     command: "npx"
  #     args: ["-y", "@anthropic/mcp-web-search"]
  # config:
  #   reasoning_effort: "high"
```

**Model format:** `provider/model` (e.g., `qwen/qwen3-coder`, `deepseek/deepseek-v3.2`, `z-ai/glm-5`)

### Codex (`codex`)

OpenAI's code execution agent, optimized for O-series reasoning models.
Supports MCP servers, skills, and custom prompt templates.

```yaml
agent:
  harness_name: "codex"
  model: "gpt-5.3-codex"
  # version: "0.1.2504171455"          # pin CLI version
  # prompt_template_path: "prompts/system.j2"
  # skills_dir: "skills/"
  # mcp_servers:
  #   - name: "filesystem"
  #     transport: "stdio"
  #     command: "npx"
  #     args: ["-y", "@anthropic/mcp-filesystem", "/app"]
  # config:
  #   reasoning_effort: "high"          # low | medium | high
```

**Supported models:** `gpt-5.4`, `gpt-5.3-codex`, `codex-mini`

### Goose (`goose`)

Code automation tool by Block with multi-provider support.
Supports MCP servers, skills, and custom prompt templates.

```yaml
agent:
  harness_name: "goose"
  model: "deepseek/deepseek-v3.2"
  # version: "stable"                  # stable | specific version
  # prompt_template_path: "prompts/system.j2"
  # skills_dir: "skills/"
  # mcp_servers:
  #   - name: "developer"
  #     transport: "stdio"
  #     command: "npx"
  #     args: ["-y", "@anthropic/mcp-developer"]
```

**Model format:** `provider/model` (e.g., `deepseek/deepseek-v3.2`, `qwen/qwen3-coder`)

### OpenHands SDK (`openhands-sdk`)

Lightweight OpenHands agent using the SDK directly. Supports MCP servers, skills, and prompt templates.

```yaml
agent:
  harness_name: "openhands-sdk"
  model: "moonshotai/kimi-k2.5"
  # prompt_template_path: "prompts/system.j2"
  # skills_dir: "skills/"
  # mcp_servers:
  #   - name: "web-search"
  #     transport: "stdio"
  #     command: "npx"
  #     args: ["-y", "@anthropic/mcp-web-search"]
  # config:
  #   reasoning_effort: "high"          # low | medium | high
  #   api_base: "https://custom.api"    # custom API endpoint
  #   model_info:
  #     max_input_tokens: 200000
  #     max_output_tokens: 16384
```

**Model format:** LiteLLM format (e.g., `moonshotai/kimi-k2.5`, `z-ai/glm-5`)

---

## Suggested Open-Source Models

These SOTA open-source models work well with Arena harness agents via OpenRouter:

| Model | Provider | Params | Strength |
|-------|----------|--------|----------|
| `moonshotai/kimi-k2.5` | Moonshot AI | 1T MoE (32B active) | Multimodal agentic coding, 100-agent swarm |
| `deepseek/deepseek-v3.2` | DeepSeek | MoE | Reasoning + tool-use, thinking mode |
| `z-ai/glm-5` | Z.ai (Zhipu) | 744B MoE (44B active) | 91.2% SWE-bench, lowest cost |
| `qwen/qwen3-coder` | Alibaba | 480B MoE (35B active) | SOTA agentic coding, free on OpenRouter |

```yaml
# Example — pick one model for your agent
agent:
  harness_name: "opencode"
  model: "qwen/qwen3-coder"                  # free, SOTA coding
  # model: "moonshotai/kimi-k2.5"             # multimodal + agent swarm
  # model: "deepseek/deepseek-v3.2"           # best reasoning + tool-use
  # model: "z-ai/glm-5"                       # highest SWE-bench, cheap
```

---

## MCP Servers

All harness agents support [Model Context Protocol](https://modelcontextprotocol.io/) servers
to extend agent capabilities with external tools (web search, file access, databases, etc.).

```yaml
agent:
  mcp_servers:
    # Local stdio server
    - name: "web-search"
      transport: "stdio"
      command: "npx"
      args: ["-y", "@anthropic/mcp-web-search"]

    # Remote SSE server
    - name: "remote-api"
      transport: "sse"
      url: "https://mcp.example.com/sse"

    # Remote streamable HTTP server
    - name: "tools"
      transport: "streamable-http"
      url: "https://mcp.example.com/mcp"
```

Each MCP server is configured per-agent at runtime — the harness translates the YAML
config into the agent's native MCP format (e.g., opencode.json, codex config.toml, goose extensions).

## Skills

Skills are reusable instruction files that augment the agent's capabilities.
Place skill files in a directory and reference it in `arena.yaml`:

```yaml
agent:
  skills_dir: "skills/"
```

The skills directory is copied into the agent's environment during setup.
Supported by all harness agents: `opencode`, `codex`, `goose`, `openhands-sdk`.

## Prompt Templates

Customize the instruction sent to the agent using Jinja2 templates:

```yaml
agent:
  prompt_template_path: "prompts/system.j2"
```

The template must contain `{{ instruction }}` where the task instruction is injected:

```jinja2
You are an expert software engineer. Follow these guidelines:
- Read files before editing
- Run tests after changes
- Write minimal, focused solutions

Task:
{{ instruction }}
```

## Development Workflow

### Iterate locally

```bash
# Run a few tasks and check results
arena test --n 3

# View detailed trajectory of the latest run
arena view

# Update sample tasks if new ones are available
arena pull
```

Results are saved to `.arena/runs/<run-id>/` with per-task rewards, latency, cost, and agent trajectories.

### Submit and track

```bash
# Submit your agent for server-side evaluation
arena submit

# Check submission status
arena status <submission-id>

# Stream live results
arena results <submission-id>

# View your ranking
arena leaderboard
```

### Compare submissions

```bash
# See history of all submissions
arena history

# Compare two submissions side-by-side
arena compare <id-1> <id-2>
```

## arena.yaml Reference

| Field | Description | Default |
|-------|-------------|---------|
| `name` | Project name (alphanumeric, hyphens, underscores) | *required* |
| `competition` | Competition slug (e.g. `officeqa`) | *required* |
| `version` | Agent version string | — |
| `description` | Project description | — |
| `tags` | List of tags for organization | `[]` |
| `agent.type` | `harness` (pre-built) or `python` (custom) | `harness` |
| `agent.harness_name` | Which harness: `opencode`, `openhands-sdk`, `codex`, `goose` | *required for harness* |
| `agent.model` | LLM model (e.g. `qwen/qwen3-coder`) | *required for harness* |
| `agent.import_path` | Python import path (e.g. `my_agent:Agent`) | *required for python* |
| `agent.version` | Pin harness CLI version | — |
| `agent.env` | Environment variables (supports `${oc.env:VAR}`) | `{}` |
| `agent.config` | Agent-specific passthrough settings | `{}` |
| `agent.prompt_template_path` | Jinja2 template for wrapping instructions | — |
| `agent.skills_dir` | Directory of reusable skill files | — |
| `agent.mcp_servers` | List of MCP server configurations | `[]` |
| `environment.memory` | Container memory limit | `4G` |
| `environment.timeout_per_task` | Max seconds per task (1–600) | `300` |
| `environment.python_version` | Python version in container | `3.11` |
| `environment.gpu` | Enable GPU | `false` |
| `environment.network` | Network mode: `sandbox` or `restricted` | `sandbox` |

## Troubleshooting

```bash
# Full health check
arena doctor

# Check competition details and quotas
arena competition officeqa
arena quota
```

**Common issues:**
- `Docker not found` — Install and start Docker Desktop
- `OPENROUTER_API_KEY not set` — Export your API key: `export OPENROUTER_API_KEY=sk-or-...`
- `Authentication failed` — Run `arena auth login` to get a valid token
- `uv lock failed` — Run `uv lock` manually or check pyproject.toml
