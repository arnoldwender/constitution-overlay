# Changelog

All notable changes to `constitution-overlay` are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.1.2] — 2026-09-10

Metadata-only release. `src/` is byte-identical to 0.1.1.

### Fixed

- **The PyPI project page said "Not on PyPI yet."** 0.1.1 was cut from the commit
  *before* the README install line was corrected, and PyPI freezes a version's
  description at upload — it cannot be replaced in place. So the page for a
  published package carried a notice saying the package was not published.

  That is precisely the failure this library exists to prevent, printed on its
  own storefront. This release re-cuts the same code from a tree whose README is
  true.

### Note for future releases

**Cut the tag after the README is correct, not before.** The README at the tagged
commit becomes the project page for that version, permanently. A doc fix merged
to `main` after the tag never reaches PyPI.

---

## [0.1.1] — 2026-09-10

First release published to PyPI. No library code changed — `src/` is byte-identical
to 0.1.0.

### Added

- `.github/workflows/release.yml` — tag-triggered release via PyPI Trusted
  Publishing (OIDC, no long-lived API token). Runs pytest, `mypy --strict` and
  `ruff` on Python 3.11/3.12/3.13, and refuses to publish when the git tag and
  the `pyproject.toml` version disagree
- `[project.urls]` — Homepage, Repository, Issues and Changelog now appear on the
  package page

### Fixed

- The README instructed `pip install constitution-overlay` while the package had
  never been published; the install line now states what actually works

### Note

`v0.1.0` is referenced by the Zenodo deposit `10.5281/zenodo.19773589`
(`IsSupplementTo` the `tree/v0.1.0` tag) and is therefore left untouched.

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
