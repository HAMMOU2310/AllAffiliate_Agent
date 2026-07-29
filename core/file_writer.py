"""
core/file_writer.py

File writing utilities.
"""

from __future__ import annotations

from pathlib import Path


class FileWriter:
    """
    Handles writing text files.
    """

    def write(
        self,
        path: str | Path,
        content: str,
        encoding: str = "utf-8",
    ) -> Path:
        """
        Write text to a file.

        Parent directories are created automatically.
        """

        file_path = Path(path)

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path.write_text(
            content,
            encoding=encoding,
        )

        return file_path