"""constitution-overlay — constitution + corrections overlay for agentic systems.

Public API:
    Constitution   — loads and merges YAML/dict layers (Kustomize-style)
    halt_on_reject — decorator that enforces rules executor-side
    PolicyReject   — exception raised when an action violates the constitution
    ConstitutionContext — read-only view passed to fixer functions
    merge_layers   — standalone deep-merge utility

See DESIGN.md for the architecture rationale.
"""

__version__ = "0.1.0"

from .constitution import Constitution
from .corrections import merge_layers
from .executor import ConstitutionContext, PolicyReject, halt_on_reject

__all__: list[str] = [
    "Constitution",
    "ConstitutionContext",
    "PolicyReject",
    "halt_on_reject",
    "merge_layers",
    "__version__",
]
