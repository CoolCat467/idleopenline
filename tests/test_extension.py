import sys
from typing import Final

import pytest

from idleopenline import extension

IS_WINDOWS: Final = sys.platform == "win32"


@pytest.mark.skipif(
    IS_WINDOWS,
    reason="Skipping Unix-specific tests on Windows",
)
def test_fileposition_parse_unix() -> None:
    assert extension.FilePosition.parse(
        "src/idleopenline/extension.py:59",
    ) == extension.FilePosition("src/idleopenline/extension.py", 59, 0, 59, 0)
    assert extension.FilePosition.parse(
        "src/idleopenline/extension.py:59:43",
    ) == extension.FilePosition(
        "src/idleopenline/extension.py",
        59,
        43,
        59,
        43,
    )
    assert extension.FilePosition.parse(
        "src/idleopenline/extension.py:59:43:60",
    ) == extension.FilePosition(
        "src/idleopenline/extension.py",
        59,
        43,
        59,
        43,
    )
    assert extension.FilePosition.parse(
        "src/idleopenline/extension.py:59:43:60:48",
    ) == extension.FilePosition(
        "src/idleopenline/extension.py",
        59,
        43,
        60,
        48,
    )
    assert extension.FilePosition.parse(
        "src/idleopenline/extension.py:59:43:60:48:103",
    ) == extension.FilePosition(
        "src/idleopenline/extension.py",
        59,
        43,
        60,
        48,
    )


@pytest.mark.skipif(
    not IS_WINDOWS,
    reason="Skipping Windows-specific tests on non-Windows platforms",
)
def test_fileposition_parse_windows() -> None:
    assert extension.FilePosition.parse(
        "C:\\path\\to\\file.py:59",
    ) == extension.FilePosition("C:\\path\\to\\file.py", 59, 0, 59, 0)
    assert extension.FilePosition.parse(
        "C:\\path\\to\\file.py:59:43",
    ) == extension.FilePosition(
        "C:\\path\\to\\file.py",
        59,
        43,
        59,
        43,
    )
    assert extension.FilePosition.parse(
        "C:\\path\\to\\file.py:59:43:60",
    ) == extension.FilePosition(
        "C:\\path\\to\\file.py",
        59,
        43,
        59,
        43,
    )
    assert extension.FilePosition.parse(
        "C:\\path\\to\\file.py:59:43:60:48",
    ) == extension.FilePosition(
        "C:\\path\\to\\file.py",
        59,
        43,
        60,
        48,
    )
    assert extension.FilePosition.parse(
        "C:\\path\\to\\file.py:59:43:60:48:103",
    ) == extension.FilePosition(
        "C:\\path\\to\\file.py",
        59,
        43,
        60,
        48,
    )


def test_fileposition_is_range() -> None:
    assert not extension.FilePosition(
        "src/idleopenline/extension.py",
        59,
        0,
        59,
        0,
    ).is_range()
    assert not extension.FilePosition(
        "src/idleopenline/extension.py",
        59,
        43,
        59,
        43,
    ).is_range()
    assert extension.FilePosition(
        "src/idleopenline/extension.py",
        59,
        43,
        60,
        48,
    ).is_range()
    assert extension.FilePosition(
        "src/idleopenline/extension.py",
        59,
        43,
        59,
        48,
    ).is_range()
    assert extension.FilePosition(
        "src/idleopenline/extension.py",
        59,
        43,
        60,
        43,
    ).is_range()
    assert extension.FilePosition(
        "src/idleopenline/extension.py",
        59,
        43,
        60,
        48,
    ).is_range()
