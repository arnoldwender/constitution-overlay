"""Tests for halt_on_reject, PolicyReject, and ConstitutionContext."""

from __future__ import annotations

import pytest

from constitution_overlay import Constitution, PolicyReject, halt_on_reject
from constitution_overlay.executor import ConstitutionContext


class TestPolicyReject:
    def test_is_exception(self) -> None:
        with pytest.raises(PolicyReject):
            raise PolicyReject("test message")

    def test_message(self) -> None:
        exc = PolicyReject("too many files")
        assert "too many files" in str(exc)

    def test_is_subclass_of_exception(self) -> None:
        assert issubclass(PolicyReject, Exception)


class TestHaltOnReject:
    def _make_c(self) -> Constitution:
        return Constitution.from_dict({"limits": {"max_files": 50}})

    def test_passes_through_on_ok(self) -> None:
        c = self._make_c()

        @halt_on_reject(c)
        def action(files: list[str]) -> int:
            return len(files)

        assert action(["a.py", "b.py"]) == 2

    def test_propagates_policy_reject(self) -> None:
        c = self._make_c()
        limit = c.get("limits.max_files")

        @halt_on_reject(c)
        def commit(files: list[str]) -> None:
            if len(files) > limit:
                raise PolicyReject(f"too many files: {len(files)} > {limit}")

        with pytest.raises(PolicyReject, match="too many files"):
            commit([f"f{i}.py" for i in range(100)])

    def test_preserves_function_name(self) -> None:
        c = self._make_c()

        @halt_on_reject(c)
        def my_action() -> None: ...

        assert my_action.__name__ == "my_action"

    def test_preserves_function_docstring(self) -> None:
        c = self._make_c()

        @halt_on_reject(c)
        def documented() -> None:
            """This function does something."""

        assert documented.__doc__ == "This function does something."

    def test_type_error_on_non_constitution(self) -> None:
        with pytest.raises(TypeError, match="Constitution"):
            halt_on_reject({"not": "a constitution"})  # type: ignore[arg-type]

    def test_other_exceptions_propagate_unchanged(self) -> None:
        c = self._make_c()

        @halt_on_reject(c)
        def broken() -> None:
            raise ValueError("not a policy error")

        with pytest.raises(ValueError, match="not a policy error"):
            broken()

    def test_return_value_preserved(self) -> None:
        c = self._make_c()

        @halt_on_reject(c)
        def compute(x: int, y: int) -> int:
            return x + y

        assert compute(3, 4) == 7

    def test_kwargs_work(self) -> None:
        c = self._make_c()

        @halt_on_reject(c)
        def action(name: str = "default") -> str:
            return name

        assert action(name="custom") == "custom"

    def test_prohibited_term_check(self) -> None:
        c = Constitution.from_dict({
            "brand": {"prohibited_terms": ["billig", "guenstigster"]},
        })

        @halt_on_reject(c)
        def write_copy(text: str) -> None:
            prohibited = c.get("brand.prohibited_terms", [])
            hits = [t for t in prohibited if t in text.lower()]
            if hits:
                raise PolicyReject(f"prohibited brand terms: {hits}")

        write_copy("Professionelle Webentwicklung in Halle (Saale)")

        with pytest.raises(PolicyReject, match="prohibited"):
            write_copy("Der billigste Webdesigner in Halle")


class TestConstitutionContext:
    def _make_ctx(self) -> ConstitutionContext:
        c = Constitution.from_dict({
            "business": {
                "legal_name": "Arnold Wender",
                "home_address": {"addressLocality": "Halle (Saale)"},
            },
        })
        return ConstitutionContext(c)

    def test_get_existing(self) -> None:
        ctx = self._make_ctx()
        assert ctx.get("business.legal_name") == "Arnold Wender"

    def test_get_nested(self) -> None:
        ctx = self._make_ctx()
        assert ctx.get("business.home_address.addressLocality") == "Halle (Saale)"

    def test_get_missing_with_default(self) -> None:
        ctx = self._make_ctx()
        assert ctx.get("business.country", "DE") == "DE"

    def test_has_present(self) -> None:
        ctx = self._make_ctx()
        assert ctx.has("business.legal_name") is True

    def test_has_missing(self) -> None:
        ctx = self._make_ctx()
        assert ctx.has("business.nonexistent") is False

    def test_require_present(self) -> None:
        ctx = self._make_ctx()
        assert ctx.require("business.legal_name") == "Arnold Wender"

    def test_require_missing_raises_policy_reject(self) -> None:
        ctx = self._make_ctx()
        with pytest.raises(PolicyReject, match="missing"):
            ctx.require("business.nonexistent")

    def test_type_error_on_non_constitution(self) -> None:
        with pytest.raises(TypeError, match="Constitution"):
            ConstitutionContext({"not": "a constitution"})  # type: ignore[arg-type]

    def test_repr(self) -> None:
        ctx = self._make_ctx()
        assert "ConstitutionContext" in repr(ctx)
