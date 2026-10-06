from __future__ import annotations

import platform

import pytest

from app.runtime import ensure_supported_python


def test_runtime_is_python_314():
    ensure_supported_python()
    assert platform.python_version().startswith("3.14.")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("3.14.8", True),
        ("3.14.9", True),
        ("3.15.0", False),
    ],
)
def test_supported_version_policy(value: str, expected: bool):
    major, minor, patch = (int(part) for part in value.split("."))
    supported = (major, minor) == (3, 14) and (major, minor, patch) >= (3, 14, 8)
    assert supported is expected
