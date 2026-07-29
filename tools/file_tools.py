"""
tools/file_tools.py

Utility class for file system operations.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from core.result import Result


class FileTools:
    """
    Provides common file system operations.

    All methods return a Result object.
    """

    def exists(self, path: str | Path) -> Result:
        try:
            path = Path(path)

            return Result.ok(
                data=path.exists(),
                message="Path checked successfully.",
                metadata={
                    "path": str(path.resolve())
                },
            )

        except Exception as ex:
            return Result.fail(
                message="Failed to check path.",
                errors=[str(ex)],
            )

    def read_text(
        self,
        path: str | Path,
        encoding: str = "utf-8",
    ) -> Result:

        try:
            path = Path(path)

            if not path.exists():
                return Result.fail(
                    message="File does not exist.",
                    errors=[str(path)],
                )

            content = path.read_text(encoding=encoding)

            return Result.ok(
                data=content,
                message="File read successfully.",
                metadata={
                    "path": str(path.resolve())
                },
            )

        except Exception as ex:
            return Result.fail(
                message="Failed to read file.",
                errors=[str(ex)],
            )

    def write_text(
        self,
        path: str | Path,
        content: str,
        encoding: str = "utf-8",
    ) -> Result:

        try:
            path = Path(path)

            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            path.write_text(
                content,
                encoding=encoding,
            )

            return Result.ok(
                data=path,
                message="File written successfully.",
                metadata={
                    "path": str(path.resolve()),
                    "size": path.stat().st_size,
                },
            )

        except Exception as ex:
            return Result.fail(
                message="Failed to write file.",
                errors=[str(ex)],
            )

    def delete(self, path: str | Path) -> Result:

        try:
            path = Path(path)

            if not path.exists():
                return Result.fail(
                    message="File does not exist.",
                    errors=[str(path)],
                )

            path.unlink()

            return Result.ok(
                message="File deleted successfully.",
            )

        except Exception as ex:
            return Result.fail(
                message="Failed to delete file.",
                errors=[str(ex)],
            )

    def copy(
        self,
        source: str | Path,
        destination: str | Path,
    ) -> Result:

        try:
            source = Path(source)
            destination = Path(destination)

            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.copy2(
                source,
                destination,
            )

            return Result.ok(
                data=destination,
                message="File copied successfully.",
            )

        except Exception as ex:
            return Result.fail(
                message="Failed to copy file.",
                errors=[str(ex)],
            )

    def move(
        self,
        source: str | Path,
        destination: str | Path,
    ) -> Result:

        try:
            source = Path(source)
            destination = Path(destination)

            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.move(
                str(source),
                str(destination),
            )

            return Result.ok(
                data=destination,
                message="File moved successfully.",
            )

        except Exception as ex:
            return Result.fail(
                message="Failed to move file.",
                errors=[str(ex)],
            )

    def list_files(
        self,
        directory: str | Path,
        pattern: str = "*",
    ) -> Result:

        try:
            directory = Path(directory)

            files = list(directory.glob(pattern))

            return Result.ok(
                data=files,
                message="Files listed successfully.",
                metadata={
                    "count": len(files)
                },
            )

        except Exception as ex:
            return Result.fail(
                message="Failed to list files.",
                errors=[str(ex)],
            )

    def file_size(
        self,
        path: str | Path,
    ) -> Result:

        try:
            path = Path(path)

            if not path.exists():
                return Result.fail(
                    message="File does not exist.",
                    errors=[str(path)],
                )

            return Result.ok(
                data=path.stat().st_size,
                message="File size retrieved successfully.",
            )

        except Exception as ex:
            return Result.fail(
                message="Failed to get file size.",
                errors=[str(ex)],
            )