"""
services/project_manager.py

Project management service.
"""

from __future__ import annotations

from pathlib import Path

from core.result import Result
from services.base_service import BaseService


class ProjectManager(BaseService):
    """
    Manage Python projects.

    This service coordinates multiple tools but does not
    perform low-level operations directly.
    """

    def project_exists(
        self,
        project_path: str | Path,
    ) -> Result:
        """
        Check whether a project exists.
        """
        return self.file_tools.exists(project_path)

    def create_directory(
        self,
        directory: str | Path,
    ) -> Result:
        """
        Create a directory.
        """

        path = Path(directory)

        try:
            path.mkdir(
                parents=True,
                exist_ok=True,
            )

            return Result.ok(
                data=path,
                message="Directory created successfully.",
            )

        except Exception as ex:
            return Result.fail(
                message="Failed to create directory.",
                errors=[str(ex)],
            )

    def create_project(
        self,
        project_path: str | Path,
    ) -> Result:
        """
        Create a new project structure.
        """

        project_path = Path(project_path)

        folders = [
            "agents",
            "core",
            "services",
            "tools",
            "workspace",
            "docs",
            "tests",
        ]

        try:
            project_path.mkdir(
                parents=True,
                exist_ok=True,
            )

            for folder in folders:
                (project_path / folder).mkdir(
                    parents=True,
                    exist_ok=True,
                )

            return Result.ok(
                data=project_path,
                message="Project created successfully.",
                metadata={
                    "folders": folders,
                },
            )

        except Exception as ex:
            return Result.fail(
                message="Failed to create project.",
                errors=[str(ex)],
            )

    def project_info(
        self,
        project_path: str | Path,
    ) -> Result:
        """
        Retrieve project information.
        """

        project_path = Path(project_path)

        if not project_path.exists():
            return Result.fail(
                message="Project does not exist.",
                errors=[str(project_path)],
            )

        folders = sorted(
            p.name
            for p in project_path.iterdir()
            if p.is_dir()
        )

        files = sorted(
            p.name
            for p in project_path.iterdir()
            if p.is_file()
        )

        return Result.ok(
            data={
                "path": str(project_path.resolve()),
                "folders": folders,
                "files": files,
            },
            message="Project information retrieved successfully.",
        )