# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About This Project

Arena CLI is a tool for building and submitting AI agents to the Sentient Labs Arena competition platform. This repo ships pre-built `.whl` wheels — there is no editable Python source here. Agent developers configure agents via `arena.yaml` and test locally via Docker.

## Common Commands

### Setup (one-time)

```bash
./install.sh                          # Install CLI into ~/.arena/venv
export PATH="$HOME/.arena/bin:$PATH"  # Add to shell (also add to ~/.zshrc or ~/.bashrc)
arena auth login                      # Authenticate
arena doctor                          # Validate Docker, auth, config
```

### Development cycle

```bash
arena test --dry-run                  # Validate arena.yaml (no Docker needed)
arena test --smoke                    # Run 1 sample task locally (Docker required)
arena test --n 5                      # Run N tasks
arena test --all                      # Run all downloaded samples
arena test --filter "officeqa-*"      # Filter by glob pattern
arena pull                            # Download latest sample tasks
arena view                            # Inspect latest run trajectory
```

### Submission

```bash
arena submit
arena status <submission-id>
arena results <submission-id>
arena history
arena compare <id-1> <id-2>
arena leaderboard
```

### Other

```bash
arena init <competition>              # Scaffold a new agent project
arena update                          # Update CLI version
arena quota                           # Check usage limits
arena cancel <submission-id>
arena competition <slug>              # Show competition details
```

## Architecture

**This repo contains pre-built wheels, not editable source.** The CLI source lives at https://github.com/sentient-agi/arena.git.

**Four-layer stack:**
- `arena_core` — Pydantic models, enums, auth, errors, config schema
- `arena_sdk` — `ArenaAgent` base class, harness wrappers (opencode/codex/goose/openhands-sdk), `TracedEnvironment`, `TracedLLMClient`, ATIF trajectory recording
- `harbor` — Docker orchestration runtime; `BaseAgent` abstract class that `ArenaAgent` extends
- `arena_cli` — Typer CLI commands, API client (httpx), project scaffolding (Jinja2 templates), Harbor runner

**Execution flow (`arena test`):**
1. CLI reads `arena.yaml` → validates via `arena_core.config.ArenaConfig`
2. Harbor runner loads sample tasks from `.arena/samples/`
3. Per task: Docker container built from `task.toml`, harness agent instantiated
4. Agent calls `solve(instruction, environment)` using `TracedLLMClient` + `TracedEnvironment`
5. Verifier runs tests in container; results + ATIF trajectory written to `.arena/runs/<run-id>/`

**Key config file — `arena.yaml`:**

```yaml
name: "my-agent"
version: "0.1.0"
competition: "grounded-reasoning"  # or "officeqa"
agent:
  type: "harness"                  # only supported type currently
  harness_name: "openhands-sdk"    # opencode | codex | goose | openhands-sdk
  model: "openrouter/moonshotai/kimi-k2.5"
  prompt_template_path: "prompts/system.j2"  # optional Jinja2 system prompt
  skills_dir: "skills/"                       # optional reusable skill files
  mcp_servers:                               # optional MCP extensions
    - name: web-search
      transport: stdio
      command: npx
      args: ["-y", "@anthropic/mcp-web-search"]
  env:
    OPENROUTER_API_KEY: "${oc.env:OPENROUTER_API_KEY,''}"
environment:
  memory: "4G"
  timeout_per_task: 300  # seconds, 1–600
  python_version: "3.11"
  gpu: false
  network: "sandbox"     # or "restricted"
```

**Custom Python agent stub** (for `agent.type: python`):

```python
from arena_sdk.agent import ArenaAgent

class MyAgent(ArenaAgent):
    @staticmethod
    def name() -> str: return "my-agent"

    async def solve(self, instruction: str, environment) -> dict:
        # self.llm — TracedLLMClient (auto-records trajectory)
        return {"metadata": {"answer": "..."}}
```

**Run output location:** `.arena/runs/<run-id>/` — contains `trajectory.json` (ATIF), `verifier-result.json`, agent/environment logs.

## Prerequisites

- Python ≥ 3.13
- `uv` package manager
- Docker (for `arena test`)
