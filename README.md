# constitution-overlay

**Kustomize-style merge of YAML rule layers + halt-on-reject enforced executor-side.**

A small, framework-agnostic Python library (~300 lines) that gives agentic systems two things:

1. A **layered constitution** — `constitution.yaml` defines invariants; `corrections.yaml` overrides specific values for the current run. Rightmost-wins merge, same semantics as Kustomize.
2. **Executor-side enforcement** — `@halt_on_reject` wraps any function. When the check inside raises `PolicyReject`, the decorator propagates it unconditionally. The LLM cannot instruct the Python runtime to swallow a `raise`.

Why this matters: LLMs ignore system prompt instructions under task pressure. An executor-side decorator cannot be bypassed. See [DESIGN.md](DESIGN.md) for the full rationale.

---

## Install

```bash
pip install constitution-overlay
```

Requires Python 3.11+. Only dependency: `pyyaml`.

---

## Quick start

```python
from constitution_overlay import Constitution, PolicyReject, halt_on_reject

# 1. Build a merged constitution from two layers
constitution = Constitution.from_layers(
    {
        "brand": {"prohibited_terms": ["cheap", "cheapest"]},
        "limits": {"max_files_per_commit": 50},
    },
    {
        "limits": {"max_files_per_commit": 200},  # override for this run
    },
)

# 2. Enforce rules executor-side
@halt_on_reject(constitution)
def commit_files(files: list[str]) -> None:
    limit = constitution.get("limits.max_files_per_commit")
    if len(files) > limit:
        raise PolicyReject(f"too many files: {len(files)} > {limit}")

commit_files(["a.py", "b.py"])  # OK
commit_files(["x.py"] * 300)    # raises PolicyReject — cannot be bypassed
```

See [examples/basic_usage.py](examples/basic_usage.py) for a complete runnable example.

---

## Load from YAML

```yaml
# constitution.yaml
brand:
  prohibited_terms:
    - cheap
    - cheapest
limits:
  max_files_per_commit: 50
  no_force_push: true
```

```yaml
# corrections.yaml
limits:
  max_files_per_commit: 200   # override for this large-batch run
```

```python
from constitution_overlay import Constitution

c = Constitution.from_layers(
    Constitution.from_yaml("constitution.yaml").rules,
    Constitution.from_yaml("corrections.yaml").rules,
)
print(c.get("limits.max_files_per_commit"))  # 200
print(c.get("limits.no_force_push"))          # True — inherited from base
```

---

## API

```python
# Load
Constitution.from_dict(d: dict) -> Constitution
Constitution.from_yaml(path: str | Path) -> Constitution
Constitution.from_layers(*layers: dict) -> Constitution   # rightmost-wins merge

# Query
c.rules                    # post-merge dict
c.get(key, default=None)   # dot-notation: "brand.prohibited_terms"
c.has(key) -> bool

# Enforce
@halt_on_reject(c)
def agent_action(...): ...   # PolicyReject raised inside propagates unconditionally

# Exceptions
class PolicyReject(Exception): ...
```

`ConstitutionContext` is also exported for use inside wrapped functions — a read-only view over `c.rules` with the same `get`/`has` interface.

---

## Merge semantics

- Dicts merge **recursively** — a later layer overrides specific keys without clobbering siblings.
- Scalars and lists are **replaced** by the rightmost value (list-append directive is on the v0.2 roadmap).
- `None` is a valid explicit value and survives the merge.
- Type mismatches raise `TypeError` immediately rather than silently coercing.

---

## Project layout

```text
src/constitution_overlay/
    __init__.py       # public exports
    constitution.py   # Constitution class + YAML loading
    corrections.py    # deep_merge + merge_layers
    executor.py       # halt_on_reject, PolicyReject, ConstitutionContext
tests/
    test_constitution.py
    test_executor.py
    test_merge.py
    test_smoke.py
examples/
    basic_usage.py
```

---

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

.venv/bin/pytest tests/ -q          # 69 tests
.venv/bin/mypy --strict src/        # must be clean
.venv/bin/ruff check src/ tests/    # must be clean
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution guide.

---

## License

MIT — see [LICENSE](LICENSE).
