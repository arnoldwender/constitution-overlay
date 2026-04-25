# Changelog

All notable changes to `constitution-overlay` are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.1.0] — 2026-04-25

First public release.

### Added

- `Constitution` class — loads and merges YAML/dict layers with Kustomize-style rightmost-wins semantics
- `Constitution.from_dict`, `from_yaml`, `from_layers` constructors
- `Constitution.get(key, default)` — dot-notation access to merged rules
- `Constitution.has(key)` — dot-notation existence check
- `deep_merge` — recursive dict merge (scalars and lists replaced, dicts merged recursively)
- `merge_layers(*layers)` — convenience alias for `Constitution.from_layers`
- `halt_on_reject(constitution)` — decorator factory; `PolicyReject` raised inside the wrapped function propagates unconditionally
- `PolicyReject` — exception type that signals a policy halt
- `ConstitutionContext` — read-only view passed to fixer functions (`get`, `has`, `require`)
- 69 tests, 98% coverage
- `mypy --strict` clean
- `ruff` clean
- `examples/basic_usage.py` — runnable end-to-end example

---

## [0.0.1] — 2026-04-25

Initial scaffold — public symbols declared, all implementation stubs.
