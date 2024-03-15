"""Open Line IDLE Extension."""

# Programmed by CoolCat467

from __future__ import annotations

# IDLE Open Line Extension
# Copyright (C) 2024  CoolCat467
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__title__ = "extension"
__author__ = "CoolCat467"
__license__ = "GNU General Public License Version 3"

from typing import TYPE_CHECKING, ClassVar, NamedTuple

from idleopenline import utils

if TYPE_CHECKING:
    from idlelib.pyshell import PyShellEditorWindow

    from typing_extensions import Self


def debug(message: object) -> None:
    """Print debug message."""
    # TODO: Censor username/user files
    print(f"\n[{__title__}] DEBUG: {message}")


def int_default(text: str, default: int = 0) -> int:
    """Return text as int or default if there is a ValueError."""
    try:
        return int(text)
    except ValueError:
        return default


class FilePosition(NamedTuple):
    """File Position."""

    path: str
    line: int
    col: int
    line_end: int
    col_end: int

    def is_range(self) -> bool:
        """Return True if file position covers a range."""
        return self.line != self.line_end or self.col != self.col_end

    def as_select(self) -> tuple[str, str]:
        """Return text selection region index strings."""
        return f"{self.line}.{self.col}", f"{self.line_end}.{self.col_end}"

    @classmethod
    def parse(cls, file_position: str) -> Self:
        """Parse file position string."""
        line = 0
        line_end = 0
        col = 0
        col_end = 0

        position = file_position.split(":", 5)

        filename = position[0]
        if len(position) > 1:
            line = int_default(position[1])
            line_end = line
        if len(position) > 2:
            col = int_default(position[2])
            col_end = col
        if len(position) > 4:
            line_end = int_default(position[3], line_end)
            col_end = int_default(position[4], col_end)

        # If line end is before beginning, swap.
        if line_end < line:
            line, line_end = line_end, line
            col, col_end = col_end, col

        return cls(
            path=filename,
            line=line,
            col=col,
            line_end=line_end,
            col_end=col_end,
        )


def goto_line_col(
    editwin: PyShellEditorWindow,
    line: int = 1,
    col: int = 0,
) -> None:
    """Go to line:col in current file."""
    editwin.text.mark_set("insert", f"{line}.{col}")
    editwin.text.tag_remove("sel", "1.0", "end")
    editwin.center()


# Important weird: If event handler function returns 'break',
# then it prevents other bindings of same event type from running.
# If returns None, normal and others are also run.


class idleopenline(utils.BaseExtension):  # noqa: N801
    """Open line from command line interface."""

    __slots__ = ()
    # Extend the file and format menus.
    menudefs: ClassVar = []
    # Default values for configuration file
    values: ClassVar = {
        "enable": "True",
        "enable_editor": "True",
        "enable_shell": "False",
    }
    # Default key binds for configuration file
    bind_defaults: ClassVar = {}

    def __init__(self, editwin: PyShellEditorWindow) -> None:
        """Initialize the settings for this extension."""
        super().__init__(editwin)

        self.reopen_file_position()

    def reopen_file_position(self) -> None:
        """Re-open IDLE correctly."""
        raw_filename: str | None = self.files.filename
        # Don't run for untitled files.
        if raw_filename is None:
            return

        position = FilePosition.parse(raw_filename)

        # Only continue if there are changes in path
        if position.path == raw_filename:
            return

        # Reload correct path
        self.editwin.io.loadfile(position.path)
        # Go to correct location in file
        goto_line_col(self.editwin, position.line, position.col)
        # If is range, select range.
        if position.is_range():
            utils.higlight_region(self.text, "sel", *position.as_select())

    # def close(self) -> None:
    #    """Called when any idle editor window closes"""
