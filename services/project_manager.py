from pathlib import Path

from core.result import Result


class ProjectManager:
    """
    مسؤول عن إنشاء وإدارة المشاريع.
    """

    def create_project(self, project_name: str):

        try:

            root = Path("workspace") / project_name

            if root.exists():

                return Result.fail(
                    message="المشروع موجود مسبقاً."
                )

            directories = (
                "src",
                "tests",
                "docs",
                "assets",
            )

            root.mkdir(
                parents=True,
                exist_ok=True,
            )

            for directory in directories:

                (root / directory).mkdir(
                    parents=True,
                    exist_ok=True,
                )

            return Result.ok(
                message=f"تم إنشاء المشروع: {project_name}",
                data={
                    "path": str(root),
                },
            )

        except Exception as e:

            return Result.fail(
                message=str(e),
            )

    def exists(self, project_name: str):

        root = Path("workspace") / project_name

        return Result.ok(
            data=root.exists(),
        )

    def list_projects(self):

        workspace = Path("workspace")

        workspace.mkdir(
            exist_ok=True,
        )

        projects = [
            p.name
            for p in workspace.iterdir()
            if p.is_dir()
        ]

        return Result.ok(
            message="تم جلب المشاريع.",
            data=projects,
        )