"""Tests for Constitution class."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from constitution_overlay import Constitution


class TestFromDict:
    def test_basic(self) -> None:
        c = Constitution.from_dict({"rules": {"max_files": 50}})
        assert c.rules == {"rules": {"max_files": 50}}

    def test_deep_copy_on_construction(self) -> None:
        original: dict[str, Any] = {"rules": {"list": [1, 2, 3]}}
        c = Constitution.from_dict(original)
        c.rules["rules"]["list"].append(4)
        assert original["rules"]["list"] == [1, 2, 3]

    def test_type_error_on_non_dict(self) -> None:
        with pytest.raises(TypeError):
            Constitution.from_dict([1, 2, 3])  # type: ignore[arg-type]

    def test_empty_dict(self) -> None:
        c = Constitution.from_dict({})
        assert c.rules == {}


class TestFromYaml:
    def test_loads_file(self, tmp_path: Path) -> None:
        config = {"business": {"legal_name": "Arnold Wender"}}
        p = tmp_path / "constitution.yaml"
        p.write_text(yaml.dump(config))
        c = Constitution.from_yaml(p)
        assert c.get("business.legal_name") == "Arnold Wender"

    def test_accepts_str_path(self, tmp_path: Path) -> None:
        p = tmp_path / "c.yaml"
        p.write_text(yaml.dump({"x": 1}))
        c = Constitution.from_yaml(str(p))
        assert c.get("x") == 1

    def test_missing_file_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            Constitution.from_yaml("/nonexistent/path.yaml")

    def test_invalid_yaml_root_raises(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.yaml"
        p.write_text("- item1\n- item2\n")
        with pytest.raises(ValueError, match="mapping"):
            Constitution.from_yaml(p)

    def test_full_schema(self, tmp_path: Path) -> None:
        config = {
            "business": {
                "model": "remote-services",
                "legal_name": "Arnold Wender",
                "home_address": {
                    "addressLocality": "Halle (Saale)",
                    "postalCode": "06110",
                    "addressCountry": "DE",
                },
            },
            "brand": {
                "prohibited_terms": ["billig", "guenstigster"],
            },
            "constraints": [
                "LocalBusiness schema MUST use home_address as address",
            ],
        }
        p = tmp_path / "full.yaml"
        p.write_text(yaml.dump(config))
        c = Constitution.from_yaml(p)
        assert c.get("business.home_address.addressLocality") == "Halle (Saale)"
        assert c.get("brand.prohibited_terms") == ["billig", "guenstigster"]


class TestFromLayers:
    def test_two_dicts_rightmost_wins(self) -> None:
        base = {"limits": {"max_files": 50}}
        overlay = {"limits": {"max_files": 200}}
        c = Constitution.from_layers(base, overlay)
        assert c.get("limits.max_files") == 200

    def test_additive_keys(self) -> None:
        base = {"a": 1}
        overlay = {"b": 2}
        c = Constitution.from_layers(base, overlay)
        assert c.get("a") == 1
        assert c.get("b") == 2

    def test_yaml_path_and_dict(self, tmp_path: Path) -> None:
        base_yaml = {"business": {"legal_name": "Acme"}}
        p = tmp_path / "base.yaml"
        p.write_text(yaml.dump(base_yaml))
        overlay = {"business": {"legal_name": "Arnold Wender"}}
        c = Constitution.from_layers(str(p), overlay)
        assert c.get("business.legal_name") == "Arnold Wender"

    def test_pathlib_path(self, tmp_path: Path) -> None:
        p = tmp_path / "layer.yaml"
        p.write_text(yaml.dump({"x": 42}))
        c = Constitution.from_layers(p, {"y": 99})
        assert c.get("x") == 42
        assert c.get("y") == 99

    def test_missing_file_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            Constitution.from_layers("/nonexistent/layer.yaml")

    def test_invalid_layer_type_raises(self) -> None:
        with pytest.raises(TypeError, match="path"):
            Constitution.from_layers(42)  # type: ignore[arg-type]

    def test_three_layers(self) -> None:
        a = {"x": 1, "y": 10}
        b = {"x": 2}
        c_layer = {"y": 20}
        c = Constitution.from_layers(a, b, c_layer)
        assert c.get("x") == 2
        assert c.get("y") == 20

    def test_no_layers(self) -> None:
        c = Constitution.from_layers()
        assert c.rules == {}


class TestGet:
    def test_top_level(self) -> None:
        c = Constitution.from_dict({"x": 1})
        assert c.get("x") == 1

    def test_nested_two_levels(self) -> None:
        c = Constitution.from_dict({"a": {"b": "value"}})
        assert c.get("a.b") == "value"

    def test_nested_three_levels(self) -> None:
        c = Constitution.from_dict({"a": {"b": {"c": "deep"}}})
        assert c.get("a.b.c") == "deep"

    def test_missing_returns_none_by_default(self) -> None:
        c = Constitution.from_dict({"x": 1})
        assert c.get("y") is None

    def test_missing_returns_custom_default(self) -> None:
        c = Constitution.from_dict({"x": 1})
        assert c.get("y", 99) == 99

    def test_partial_path_missing(self) -> None:
        c = Constitution.from_dict({"a": {"b": 1}})
        assert c.get("a.c.d") is None

    def test_none_value(self) -> None:
        c = Constitution.from_dict({"key": None})
        assert c.get("key") is None

    def test_empty_string_default(self) -> None:
        c = Constitution.from_dict({})
        assert c.get("missing", "") == ""


class TestHas:
    def test_present_scalar(self) -> None:
        c = Constitution.from_dict({"x": 1})
        assert c.has("x") is True

    def test_missing_key(self) -> None:
        c = Constitution.from_dict({"x": 1})
        assert c.has("y") is False

    def test_nested_present(self) -> None:
        c = Constitution.from_dict({"a": {"b": 1}})
        assert c.has("a.b") is True

    def test_nested_missing(self) -> None:
        c = Constitution.from_dict({"a": {"b": 1}})
        assert c.has("a.c") is False

    def test_none_value_is_present(self) -> None:
        # has() reports True even when the value is explicitly None
        c = Constitution.from_dict({"key": None})
        assert c.has("key") is True

    def test_partial_path_missing(self) -> None:
        c = Constitution.from_dict({"a": 1})
        assert c.has("a.b") is False


class TestRepr:
    def test_repr_shows_top_keys(self) -> None:
        c = Constitution.from_dict({"business": {}, "brand": {}, "limits": {}})
        r = repr(c)
        assert "Constitution" in r
        assert "business" in r
