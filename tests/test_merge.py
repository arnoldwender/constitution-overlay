"""Tests for the deep-merge logic in corrections.py."""

from __future__ import annotations

import pytest

from constitution_overlay.corrections import deep_merge, merge_layers


class TestDeepMerge:
    def test_empty(self) -> None:
        assert deep_merge() == {}

    def test_single_layer(self) -> None:
        assert deep_merge({"a": 1}) == {"a": 1}

    def test_scalar_rightmost_wins(self) -> None:
        assert deep_merge({"a": 1}, {"a": 2}) == {"a": 2}

    def test_new_key_from_overlay(self) -> None:
        assert deep_merge({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}

    def test_dict_recursive_merge(self) -> None:
        base = {"x": {"a": 1, "b": 2}}
        overlay = {"x": {"b": 99, "c": 3}}
        assert deep_merge(base, overlay) == {"x": {"a": 1, "b": 99, "c": 3}}

    def test_list_rightmost_replaces(self) -> None:
        base = {"terms": ["billig", "guenstigster"]}
        overlay = {"terms": ["cheap"]}
        result = deep_merge(base, overlay)
        assert result["terms"] == ["cheap"]

    def test_none_wins(self) -> None:
        result = deep_merge({"key": "value"}, {"key": None})
        assert result["key"] is None

    def test_three_layers(self) -> None:
        a = {"x": 1, "y": {"a": 1}}
        b = {"x": 2, "y": {"b": 2}}
        c = {"x": 3}
        assert deep_merge(a, b, c) == {"x": 3, "y": {"a": 1, "b": 2}}

    def test_deep_copy_isolation(self) -> None:
        base = {"nested": {"list": [1, 2, 3]}}
        result = deep_merge(base)
        result["nested"]["list"].append(4)
        assert base["nested"]["list"] == [1, 2, 3]

    def test_type_error_on_non_dict_layer(self) -> None:
        with pytest.raises(TypeError, match="dicts"):
            deep_merge([1, 2, 3])  # type: ignore[arg-type]

    def test_deeply_nested(self) -> None:
        a = {"a": {"b": {"c": {"d": 1}}}}
        b = {"a": {"b": {"c": {"e": 2}}}}
        result = deep_merge(a, b)
        assert result == {"a": {"b": {"c": {"d": 1, "e": 2}}}}

    def test_scalar_overrides_dict(self) -> None:
        # When a later layer puts a scalar where an earlier layer had a dict,
        # the scalar wins (rightmost wins unconditionally for non-dict values).
        result = deep_merge({"x": {"a": 1}}, {"x": "scalar"})
        assert result["x"] == "scalar"

    def test_dict_overrides_scalar(self) -> None:
        result = deep_merge({"x": "scalar"}, {"x": {"a": 1}})
        assert result["x"] == {"a": 1}


class TestMergeLayersAlias:
    def test_alias_works(self) -> None:
        assert merge_layers({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}

    def test_empty(self) -> None:
        assert merge_layers() == {}
