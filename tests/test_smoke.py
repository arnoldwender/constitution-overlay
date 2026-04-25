"""Smoke test — verifies the package is importable.

[TODO] expand with real tests once Constitution + halt_on_reject are implemented.
"""

import constitution_overlay


def test_version_exposed() -> None:
    assert constitution_overlay.__version__ == "0.0.1"
