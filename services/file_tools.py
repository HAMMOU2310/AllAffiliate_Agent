from pathlib import Path

from core.result import Result


class FileTools:
    """
    خدمات التعامل مع الملفات.
    """

    def read_file(self, path: str) -> Result:

        file = Path(path)

        if not file.exists():
            return Result.fail(
                message="الملف غير موجود."
            )

        return Result.ok(
            data=file.read_text(encoding="utf-8"),
            message=f"تمت قراءة الملف: {path}",
        )

    def write_file(self, path: str, content: str) -> Result:

        file = Path(path)

        file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file.write_text(
            content,
            encoding="utf-8",
        )

        return Result.ok(
            message=f"تم حفظ الملف: {path}",
        )

    def append_file(self, path: str, content: str) -> Result:

        file = Path(path)

        file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(file, "a", encoding="utf-8") as f:
            f.write(content)

        return Result.ok(
            message=f"تمت إضافة المحتوى إلى: {path}",
        )

    def delete_file(self, path: str) -> Result:

        file = Path(path)

        if not file.exists():
            return Result.fail(
                message="الملف غير موجود."
            )

        file.unlink()

        return Result.ok(
            message=f"تم حذف الملف: {path}",
        )

    def list_files(self, path: str = "workspace") -> Result:

        folder = Path(path)

        if not folder.exists():
            return Result.fail(
                message="المجلد غير موجود."
            )

        files = [
            item.name
            for item in folder.iterdir()
            if item.is_file()
        ]

        return Result.ok(
            data=files,
            message="تم جلب الملفات.",
        )