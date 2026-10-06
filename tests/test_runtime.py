from __future__ import annotations

import platform

from app.runtime import ensure_supported_python


def test_runtime_is_python_314():
    ensure_supported_python()
    assert platform.python_version().startswith("3.14.")


def test_current_patch_is_at_least_3148():
    major, minor, patch = (int(part) for part in platform.python_version().split("."))
    assert (major, minor) == (3, 14)
    assert (major, minor, patch) >= (3, 14, 8)
