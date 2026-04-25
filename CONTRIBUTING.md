# Contributing

Contributions are welcome. Please read this before opening a PR.

## Ground rules

1. **Keep `src/` under 500 lines total.** This is a feature, not a limit to work around.
2. **No framework dependencies.** No Anthropic SDK, no LangGraph, no OpenAI. Pure policy + enforcement.
3. **Tests before features.** Each new public symbol gets a test before going into `__all__`.
4. **`mypy --strict` must pass** on every commit.
5. **`ruff check` must pass** on every commit.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Running checks

```bash
.venv/bin/pytest tests/ -q
.venv/bin/mypy --strict src/
.venv/bin/ruff check src/ tests/
```

All three must be clean before submitting a PR.

## Commit format

```
[Action] Brief description
```

Examples: `[Fix] Correct default direction in query_entity`, `[Feat] Add dry_run mode to halt_on_reject`

## What to contribute

Good first contributions:

- Bug reports with a minimal reproducer
- Fixes for issues in the tracker
- Improvements to `examples/basic_usage.py`
- Documentation clarifications in `DESIGN.md`

Not in scope for v0.1:

- Async wrappers (planned for v0.2)
- List-append merge directives (planned for v0.2)
- Framework-specific integrations (Anthropic SDK, LangGraph recipes)

## License

By contributing you agree that your work is licensed under MIT.
