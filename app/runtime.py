from __future__ import annotations

import platform
import sys


SUPPORTED_MAJOR_MINOR = (3, 14)
RECOMMENDED_VERSION = (3, 14, 8)


def ensure_supported_python() -> None:
    """Fail early with a clear message when the CLI uses an unsupported Python."""
    running = sys.version_info[:3]

    if running[:2] != SUPPORTED_MAJOR_MINOR:
        raise RuntimeError(
            "Job-Applyer 2.x requires CPython 3.14.x. "
            f"Detected Python {platform.python_version()}."
        )

    if running < RECOMMENDED_VERSION:
        raise RuntimeError(
            "Job-Applyer 2.x requires Python 3.14.8 or newer within the 3.14 series. "
            f"Detected Python {platform.python_version()}."
        )

    if sys.implementation.name != "cpython":
        raise RuntimeError(
            "Job-Applyer 2.x is tested on CPython 3.14.x. "
            f"Detected implementation: {sys.implementation.name}."
        )
