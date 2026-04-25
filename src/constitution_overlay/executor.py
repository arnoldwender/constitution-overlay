"""Executor — halt-on-reject enforcement.

The check lives in the executor code, not in the LLM prompt. The LLM cannot
bypass it — even under adversarial input that overrides instructions, the
Python decorator still raises PolicyReject and the action does not execute.
"""

from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    from .constitution import Constitution

F = TypeVar("F", bound=Callable[..., Any])


class PolicyReject(Exception):
    """Raised when an action violates the constitution. Halts the executor."""


class ConstitutionContext:
    """Read-only view of a merged constitution passed to fixer functions.

    Provides typed accessors so fixers can check business constraints
    (address, brand terms, prohibited ops) without importing Constitution.
    """

    def __init__(self, constitution: "Constitution") -> None:
        from .constitution import Constitution as _Constitution

        if not isinstance(constitution, _Constitution):
            raise TypeError(
                f"expected Constitution, got {type(constitution).__name__}"
            )
        self._c = constitution

    def get(self, key: str, default: Any = None) -> Any:
        """Dotted-key lookup delegated to the underlying constitution."""
        return self._c.get(key, default)

    def has(self, key: str) -> bool:
        """True if the key is present (even when the value is None)."""
        return self._c.has(key)

    def require(self, key: str) -> Any:
        """Return the value at `key`, or raise PolicyReject if the key is absent."""
        if not self.has(key):
            raise PolicyReject(f"required constitution key is missing: {key!r}")
        return self.get(key)

    def __repr__(self) -> str:
        return f"ConstitutionContext({self._c!r})"


def halt_on_reject(constitution: "Constitution") -> Callable[[F], F]:
    """Decorator factory that enforces the constitution executor-side.

    Wrap any agent action with this decorator. If the wrapped function raises
    `PolicyReject`, the exception propagates unconditionally — execution halts
    and the caller must handle the rejection.

    The LLM cannot bypass this: the check lives in executor code, not in the
    prompt. Prompt instructions can be overridden; a Python raise cannot.

    Usage:
        @halt_on_reject(constitution)
        def commit_files(files: list[str]) -> None:
            limit = constitution.get("limits.max_files_per_commit", 50)
            if len(files) > limit:
                raise PolicyReject(f"too many files: {len(files)} > {limit}")
    """
    from .constitution import Constitution as _Constitution

    if not isinstance(constitution, _Constitution):
        raise TypeError(
            f"halt_on_reject expects a Constitution; got {type(constitution).__name__}"
        )

    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # PolicyReject propagates unconditionally — do not catch here.
            return fn(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
