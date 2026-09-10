# constitution-overlay — Gemini (Antigravity) instructions

**Author:** Arnold Wender <arnoldwender@users.noreply.github.com>

Repo-scoped context for Gemini / Antigravity. The authoritative rules for this
repository live in [`CLAUDE.md`](CLAUDE.md) — read that first; this file only
restates what an agent needs before touching code.

## What this repo is

A small Python library (~300 lines) implementing the **constitution + corrections
overlay** pattern for agentic systems: Kustomize-style merge of YAML rule layers,
with halt-on-reject enforced executor-side via `PolicyReject`.

## Rules

1. **Keep it small.** `src/` stays under 500 lines total. Push back if it grows past that.
2. **No framework dependencies.** The library stays agnostic — no Anthropic SDK, no
   LangGraph, no OpenAI. Pure policy + enforcement layer.
3. **MIT license.** Do not change.
4. **Tests before features.** Each public symbol gets a test before going into `__all__`.
5. **Type hints everywhere.** `mypy --strict` must pass on every commit.

## Workflow

- Commit format: `[Action] Brief description`
- No co-author tags, no AI branding

## Quick check

```bash
.venv/bin/pytest tests/ -q          # 69 tests, should all pass
.venv/bin/mypy --strict src/        # must be clean
.venv/bin/ruff check src/ tests/    # must be clean
```
