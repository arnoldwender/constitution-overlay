"""Constitution — base loader + queryable rule object."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

from .corrections import merge_layers


class Constitution:
    """Holds the merged ruleset. Constructed from one or more layers.

    Example:
        base = {"limits": {"max_files_per_commit": 50}}
        overlay = {"limits": {"max_files_per_commit": 200}}
        c = Constitution.from_layers(base, overlay)
        c.get("limits.max_files_per_commit")  # 200
    """

    def __init__(self, rules: dict[str, Any]) -> None:
        if not isinstance(rules, dict):
            raise TypeError(f"rules must be a dict; got {type(rules).__name__}")
        self._rules: dict[str, Any] = rules

    @property
    def rules(self) -> dict[str, Any]:
        """Post-merge rule dict. Read-only by convention."""
        return self._rules

    # -- Constructors -------------------------------------------------------

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Constitution":
        """Return a Constitution wrapping a deep copy of `d`."""
        if not isinstance(d, dict):
            raise TypeError(f"expected dict, got {type(d).__name__}")
        return cls(copy.deepcopy(d))

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Constitution":
        """Load YAML at `path` and return a Constitution."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"constitution file not found: {p}")
        with p.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if not isinstance(data, dict):
            raise ValueError(
                f"constitution YAML must be a mapping; got {type(data).__name__}"
            )
        return cls(data)

    @classmethod
    def from_layers(cls, *layers: "dict[str, Any] | str | Path") -> "Constitution":
        """Kustomize-style merge of layers in order.

        Each layer may be a dict or a YAML file path (str or Path).
        Later layers override earlier ones (rightmost wins).
        """
        resolved: list[dict[str, Any]] = []
        for layer in layers:
            if isinstance(layer, (str, Path)):
                p = Path(layer)
                if not p.exists():
                    raise FileNotFoundError(f"layer file not found: {p}")
                with p.open(encoding="utf-8") as fh:
                    d = yaml.safe_load(fh)
                if not isinstance(d, dict):
                    raise ValueError(f"YAML layer at {p} must be a mapping")
                resolved.append(d)
            elif isinstance(layer, dict):
                resolved.append(layer)
            else:
                raise TypeError(
                    f"layer must be a dict or file path; got {type(layer).__name__}"
                )
        return cls(merge_layers(*resolved))

    # -- Querying -----------------------------------------------------------

    def get(self, key: str, default: Any = None) -> Any:
        """Dotted-key lookup.

        Example: c.get("business.home_address.addressLocality")
        Returns `default` if any segment is missing.
        """
        parts = key.split(".")
        node: Any = self._rules
        for part in parts:
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def has(self, key: str) -> bool:
        """True if the dotted key is present (even when the value is None)."""
        parts = key.split(".")
        node: Any = self._rules
        for part in parts:
            if not isinstance(node, dict) or part not in node:
                return False
            node = node[part]
        return True

    def __repr__(self) -> str:
        top_keys = list(self._rules.keys())[:5]
        return f"Constitution(top_keys={top_keys!r})"
