"""Open Line IDLE Extension."""

# Programmed by CoolCat467

from __future__ import annotations

# IDLE Open Line Extension
# Copyright (C) 2024-2025  CoolCat467
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

import sys
from idlelib.config import idleConf
from pathlib import Path
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

        windows_drive_letter = ""
        if sys.platform == "win32":
            windows_drive_letter, file_position = file_position.split(":", 1)
            windows_drive_letter += ":"
        position = file_position.rsplit(":", 5)

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
            path=f"{windows_drive_letter}{filename}",
            line=line,
            col=col,
            line_end=line_end,
            col_end=col_end,
        )

    def serialize(self) -> str:
        """Return file position as string."""
        if self.is_range():
            return f"{self.path}:{self.line}:{self.col}:{self.line_end}:{self.col_end}"
        if self.col != 0:
            return f"{self.path}:{self.line}:{self.col}"
        return f"{self.path}:{self.line}"

    @classmethod
    def from_editor_current(cls, editwin: PyShellEditorWindow) -> Self | None:
        """Return file position from editwin current position."""
        current_filename = editwin.io.filename
        if current_filename is None:
            return None
        current_filename = str(Path(current_filename).absolute())
        selected = utils.get_selected_text_indexes(editwin.text)
        select_string = (":".join(selected)).replace(".", ":")
        return cls.parse(f"{current_filename}:{select_string}")


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
        "save_last_position": "False",
    }
    # Default key binds for configuration file
    bind_defaults: ClassVar = {}

    save_last_position: str = "False"

    idlerc_folder = Path(idleConf.userdir).expanduser().absolute()
    last_position_file = idlerc_folder / "last-positions.lst"

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
            if self.save_last_position != "True":
                return
            if not self.last_position_file.exists():
                return
            for line in self.last_position_file.read_text(
                encoding="utf-8",
            ).splitlines():
                if raw_filename in line:
                    position = FilePosition.parse(line)
                    break
        else:
            # Reload correct path
            self.editwin.io.loadfile(position.path)

        # Go to correct location in file
        goto_line_col(self.editwin, position.line, position.col)
        # If is range, select range.
        if position.is_range():
            utils.highlight_region(self.text, "sel", *position.as_select())

    def save_current_position(self) -> None:
        """Save current position position."""
        position = FilePosition.from_editor_current(self.editwin)

        if position is None:
            return
        if self.last_position_file.exists():
            current_entries = self.last_position_file.read_text(
                encoding="utf-8",
            ).splitlines()
        else:
            current_entries = []

        for idx, entry in reversed(tuple(enumerate(current_entries))):
            if position.path in entry:
                del current_entries[idx]

        current_entries.insert(0, position.serialize())

        current_entries = current_entries[:21]
        with self.last_position_file.open("w", encoding="utf-8") as fp:
            fp.write("\n".join(current_entries))

    @utils.log_exceptions_catch
    def close(self) -> None:
        """Handle when any idle editor window closes."""
        if self.save_last_position != "True":
            return
        self.save_current_position()
