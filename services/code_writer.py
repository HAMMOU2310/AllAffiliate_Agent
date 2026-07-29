"""
services/code_writer.py

Code writing service.
"""

from __future__ import annotations

from pathlib import Path

from core.result import Result
from services.base_service import BaseService


class CodeWriter(BaseService):
    """
    Service responsible for creating and updating source code files.

    This service contains the business logic for code generation,
    while FileTools performs the actual file system operations.
    """

    def create_python_file(
        self,
        file_path: str | Path,
        content: str = "",
    ) -> Result:
        """
        Create a new Python file.
        """

        path = Path(file_path)

        if path.exists():
            return Result.fail(
                message="File already exists.",
                errors=[str(path)],
            )

        return self.file_tools.write_text(path, content)

    def overwrite_file(
        self,
        file_path: str | Path,
        content: str,
    ) -> Result:
        """
        Replace the entire file content.
        """

        return self.file_tools.write_text(file_path, content)

    def append_to_file(
        self,
        file_path: str | Path,
        content: str,
    ) -> Result:
        """
        Append text to an existing file.
        """

        read_result = self.file_tools.read_text(file_path)

        if read_result.failed:
            return read_result

        new_content = read_result.data + content

        return self.file_tools.write_text(
            file_path,
            new_content,
        )

    def ensure_directory(
        self,
        directory: str | Path,
    ) -> Result:
        """
        Ensure a directory exists.
        """

        try:
            Path(directory).mkdir(
                parents=True,
                exist_ok=True,
            )

            return Result.ok(
                data=Path(directory),
                message="Directory is ready.",
            )

        except Exception as ex:
            return Result.fail(
                message="Failed to create directory.",
                errors=[str(ex)],
            )