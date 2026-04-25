"""Corrections — Kustomize-style merge of overlays.

Rules (Kustomize strategic-merge semantics, rightmost wins):
- dicts: merged recursively; rightmost value wins per key.
- lists: rightmost list replaces the earlier one (not appended).
- scalars: rightmost wins.
- None in a later layer explicitly sets the value to None.

Deterministic given the layer order. No LLM-driven merge — debuggability
requires the same input always producing the same output.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def deep_merge(*layers: dict[str, Any]) -> dict[str, Any]:
    """Deep-merge dicts left-to-right; rightmost value wins at each key.

    Dicts are merged recursively. Lists and scalars are replaced by the
    rightmost value. A later layer may explicitly set a key to None.
    """
    if not layers:
        return {}

    result: dict[str, Any] = {}
    for layer in layers:
        if not isinstance(layer, dict):
            raise TypeError(f"all layers must be dicts; got {type(layer).__name__}")
        for key, value in layer.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = deepcopy(value)
    return result


def merge_layers(*layers: dict[str, Any]) -> dict[str, Any]:
    """Merge constitution layers in order. Public alias for deep_merge."""
    return deep_merge(*layers)
