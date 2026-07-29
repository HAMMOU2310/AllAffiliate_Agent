from pathlib import Path

from core.result import Result


class FileTools:
    """
    Utility class for file system operations.
    """

    def exists(self, path: str | Path) -> Result:
        ...

    def read_text(
        self,
        path: str | Path,
        encoding: str = "utf-8",
    ) -> Result:
        ...

    def write_text(
        self,
        path: str | Path,
        content: str,
        encoding: str = "utf-8",
    ) -> Result:
        ...

    def delete(self, path: str | Path) -> Result:
        ...

    def copy(
        self,
        source: str | Path,
        destination: str | Path,
    ) -> Result:
        ...

    def move(
        self,
        source: str | Path,
        destination: str | Path,
    ) -> Result:
        ...

    def list_files(
        self,
        directory: str | Path,
        pattern: str = "*",
    ) -> Result:
        ...

    def file_size(self, path: str | Path) -> Result:
        ...