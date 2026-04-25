# Design — constitution + corrections overlay

This document is the architecture rationale for `constitution-overlay`. It is also the seed for the public blog post that accompanies the v0.1 release.

## 1. The problem

When you run an LLM agent over a real codebase, you need it to respect rules. Not suggestions — rules. "This is the legal business address; never substitute a target-market address." "No force pushes." "Never write these prohibited brand terms in copy." "LocalBusiness schema must use the home address, not the service area."

The obvious approach is to put the rules in the system prompt. The problem is that LLMs ignore system prompt instructions under task pressure, under adversarial input, or simply by accident. This is documented and reproducible. Claude Code issue [#19874](https://github.com/anthropics/claude-code/issues/19874) states it plainly: Plan Mode provides no actual enforcement of read-only restrictions — the safety guarantee is implemented purely as a system prompt instruction that the LLM can and regularly does ignore.

The right fix is not a better prompt. It is enforcement at the executor layer — a check in code that the LLM cannot override. And for teams managing multiple agents or environments, that enforcement layer needs to be *configurable*: base invariants that never change, plus per-run corrections that adjust specific values without touching the base.

Concrete framing:

- LLM agents need two layers: invariants the agent must respect, and overlays that adjust those invariants per context (repo, user, task).
- Plan Mode (Claude Code) addresses *proposal time* — review-before-edit. It does not enforce *execution time* halts.
- Existing frameworks (LangGraph, CrewAI, AutoGen) provide nodes/edges but no opinionated policy merging.
- Bedrock Guardrails enforces at runtime but is single-layer and tied to AWS.
- Kustomize solves the *layered config* problem for Kubernetes but is not designed for agentic systems.

The gap: a small, framework-agnostic library that combines Kustomize-style merge with halt-on-reject enforcement at the executor layer.

## 2. Prior art

| System | What it does well | What's missing for agentic policy |
|---|---|---|
| **Kustomize** | Strategic merge, list patches, named overrides | Not LLM-aware; not callable as a runtime check |
| **Spec Kit** | Schemas + validation | Static; no runtime enforcement |
| **Bedrock Guardrails** | Runtime guardrails | Single-layer; AWS-bound |
| **LangGraph** | Stateful orchestration | No opinionated policy layer |
| **Claude Code Plan Mode** | Proposal review | No halt-on-reject at execution |
| **OpenAI Custom GPTs** | Toolkit + persona | No multi-layer constitution |

Kustomize patches (strategic merge, JSON patches) are the canonical reference for rightmost-wins layered config in the infra world. Spec Kit's `memory/constitution.md` is the closest prior art in the LLM space: a non-negotiable principles file loaded as context before lifecycle commands. The naming is right; the enforcement is not there — context injection is not the same as a code-level halt.

## 3. The convergence proposed

Kustomize solves "I have a base config and I need per-environment corrections" with a deterministic rightmost-wins merge. Base defines defaults; overlays override specific fields; the result is reproducible without any logic-driven merge. Applied to agent policy, the shape maps directly: `constitution.yaml` defines invariants, `corrections.yaml` holds per-run overrides, `Constitution.from_layers()` produces the merged view.

The second piece is enforcement. Once the merged rules exist in memory, a `@halt_on_reject(constitution)` decorator wraps executor functions. When a policy check inside the function raises `PolicyReject`, the decorator lets it propagate unconditionally — nothing can swallow it. The LLM cannot instruct the Python runtime to skip a `raise`. This is the backstop that prompt-only approaches lack.

The combination — deterministic layered merge plus executor-side halt — is what makes this a primitive rather than a pattern. It is a boundary that can be placed around any agent action regardless of which framework orchestrates it.

Key claims to defend:

1. **Kustomize-style merge is the right shape** for layering constitution + corrections because it is order-aware, list-aware, and well-understood by ops engineers.
2. **Halt-on-reject must be enforced executor-side**, not via prompt instructions. LLMs ignore prompt instructions under adversarial input; an executor-side decorator/wrapper cannot be bypassed.
3. **Framework-agnostic** is the correct scope. The library should not depend on Anthropic SDK, OpenAI SDK, or any single agent framework. It should be a pure policy + enforcement layer.
4. **Small** is a feature. The reference implementation aims at ~500 lines so it can be read end-to-end in one sitting.

## 4. Architecture

```
┌──────────────────────────────────────┐
│ user task                            │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│ Constitution.from_layers(            │
│   base_yaml,                         │
│   corrections_yaml,                  │
│   ... runtime overlays               │
│ )                                    │
│                                      │
│ → merged in Kustomize style          │
│ → exposes .rules dict                │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│ @halt_on_reject(constitution)        │
│ def agent_action(...):               │
│     # checks before/around the call  │
│     # raises PolicyReject if blocked │
│     ...                              │
└──────────────────────────────────────┘
```

**Merge semantics** (`deep_merge` in `corrections.py`):

- Dicts merge recursively — later layers override specific keys without clobbering siblings.
- Scalars and lists are replaced by the rightmost value — no append logic in v0.1.
- `None` is a valid explicit value — it survives the merge and does not trigger a "missing" branch.
- Type errors raise immediately (`TypeError`) rather than silently coercing.

**`halt_on_reject` plugs into agent actions** by wrapping the function that executes the action. The check lives inside the wrapped function (authored by the developer); the decorator enforces that `PolicyReject` is never swallowed. `ConstitutionContext` can be passed into the wrapped function to give it clean `get`/`has`/`require` access to the merged rules without exposing the full `Constitution` internals.

## 5. API surface

```python
# Loading
Constitution.from_dict(d: dict) -> Constitution
Constitution.from_yaml(path: str | Path) -> Constitution
Constitution.from_layers(*layers) -> Constitution

# Querying
c.rules             # dict-like, post-merge
c.get(key, default)
c.has(key)

# Enforcement
@halt_on_reject(c)
def fn(...): ...

# Errors
class PolicyReject(Exception): ...
```

The public surface as of v0.1 is locked to four symbols exported from `constitution_overlay`:

```python
from constitution_overlay import (
    Constitution,        # loads and merges YAML/dict layers
    halt_on_reject,      # decorator factory — marks enforcement boundary
    PolicyReject,        # exception type — signals a policy halt
    ConstitutionContext, # read-only view for use inside wrapped functions
)
```

`merge_layers` is also exported as a convenience alias for `Constitution.from_layers` when callers only need the merge without the full object. Internal modules (`corrections`, `constitution`, `executor`) are not part of the public surface.

## 6. Non-goals

- Not a replacement for LangGraph, CrewAI, or Claude Agent SDK.
- Not an attempt at "agent safety" in the broad sense — focused narrowly on policy layering and enforcement.
- Not a UI / dashboard. Just a library.
- Not async-first in v0.1 (sync only — async wrappers come later).

## 7. Open questions

- **Conflicting overlays** — resolved: last-write-wins (rightmost layer). No explicit merge directives in v0.1. This keeps the merge semantics identical to Kustomize's strategic merge for scalars and dicts. The only open sub-question is list append vs replace: v0.1 replaces, v0.2 will add an append directive.
- **`halt_on_reject` predicate** — resolved for v0.1: checks live inside the wrapped function, not in the decorator. The decorator is a contract marker only. Callable predicate support is on the v0.2 roadmap.
- **`dry_run` mode** — deferred to v0.2. Would log would-have-rejected rejections without raising. Useful for gradual rollout.
- **Distribution** — PyPI from day 1, reserved as `constitution-overlay`. Package name verified available at time of v0.1 release.

## 8. Roadmap

- **v0.0.1** — scaffold (initial commit).
- **v0.1.0** — working merge + halt_on_reject + 1 realistic example + 98% test coverage. Public release + blog post. **[released 2026-04-25]**
- **v0.2.0** — async wrappers, more merge directives, integration recipes for Anthropic SDK + LangGraph.
- **v1.0.0** — API stable, deployed in production by ≥3 outside users.
