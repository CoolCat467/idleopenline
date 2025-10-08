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
from typing import TYPE_CHECKING, ClassVar

from idleopenline import utils

if TYPE_CHECKING:
    from collections.abc import Sequence
    from idlelib.pyshell import PyShellEditorWindow


def debug(message: object) -> None:
    """Print debug message."""
    # TODO: Censor username/user files
    print(f"\n[{__name__}] DEBUG: {message}")


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
    menudefs: ClassVar[
        Sequence[tuple[str, Sequence[tuple[str, str] | None]]]
    ] = []
    # Default values for configuration file
    values: ClassVar = {
        "enable": "True",
        "enable_editor": "True",
        "enable_shell": "False",
        "save_last_position": "False",
        "max_entries": "21",
    }
    # Default key binds for configuration file
    bind_defaults: ClassVar = {}

    save_last_position: str = "False"
    max_entries: int = 21

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

        position = utils.FilePosition.parse(raw_filename)

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
                    position = utils.FilePosition.parse(line)
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
        self.reload()

        position = utils.FilePosition.from_editor_current(self.editwin)

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
                continue
            if ":" not in entry:
                del current_entries[idx]
                continue
            try:
                if sys.platform == "win32":
                    path = ":".join(entry.split(":", 2)[1:])
                else:
                    path = entry.split(":", 1)[0]
            except Exception as exc:
                utils.extension_log_exception(exc)
                del current_entries[idx]
                continue
            try:
                if not Path(path).exists():
                    debug(f"{path = } not exists")
                    del current_entries[idx]
                    continue
            except Exception as exc:
                utils.extension_log_exception(exc)
                del current_entries[idx]
                continue

        current_entries.insert(0, position.serialize())

        current_entries = current_entries[: int(self.max_entries)]
        with self.last_position_file.open("w", encoding="utf-8") as fp:
            fp.write("\n".join(current_entries))

    @utils.log_exceptions_catch
    def close(self) -> None:
        """Handle when any idle editor window closes."""
        if self.save_last_position != "True":
            return
        self.save_current_position()
