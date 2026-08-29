from pathlib import Path

from core.result import Result


class CodeWriter:
    """
    مسؤول عن إنشاء وكتابة الملفات داخل المشروع.
    """

    def create_file(self, path: str, content: str = "") -> Result:
        try:
            file_path = Path(path)

            file_path.parent.mkdir(parents=True, exist_ok=True)

            file_path.write_text(content, encoding="utf-8")

            return Result.ok(
                message=f"تم إنشاء الملف: {file_path}",
                data={
                    "path": str(file_path),
                },
            )

        except Exception as e:
            return Result.fail(
                message=str(e)
            )

    def write_file(self, path: str, content: str) -> Result:
        try:
            file_path = Path(path)

            file_path.parent.mkdir(parents=True, exist_ok=True)

            file_path.write_text(content, encoding="utf-8")

            return Result.ok(
                message=f"تمت كتابة الملف: {file_path}",
                data={
                    "path": str(file_path),
                },
            )

        except Exception as e:
            return Result.fail(
                message=str(e)
            )

    def append_file(self, path: str, content: str) -> Result:
        try:
            file_path = Path(path)

            file_path.parent.mkdir(parents=True, exist_ok=True)

            with file_path.open("a", encoding="utf-8") as f:
                f.write(content)

            return Result.ok(
                message=f"تم تحديث الملف: {file_path}",
                data={
                    "path": str(file_path),
                },
            )

        except Exception as e:
            return Result.fail(
                message=str(e)
            )