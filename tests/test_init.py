"""Test __init__.py."""

import idleopenline


def extension_exists() -> None:
    assert hasattr(idleopenline, "idleopenline")
    assert idleopenline.__title__ == "idleopenline"


def check_installed_exists() -> None:
    assert hasattr(idleopenline, "check_installed")
    assert callable(
        idleopenline.check_installed,
    )
