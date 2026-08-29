from pathlib import Path

from core.result import Result


class TextEditor:
    """
    خدمة مسؤولة عن تعديل الملفات النصية.
    """

    def write(self, filepath: str, content: str):

        try:

            path = Path(filepath)

            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            path.write_text(
                content,
                encoding="utf-8",
            )

            return Result.ok(
                message=f"تمت كتابة الملف: {filepath}",
            )

        except Exception as e:

            return Result.fail(
                message=str(e),
            )

    def append(self, filepath: str, content: str):

        try:

            path = Path(filepath)

            with open(
                path,
                "a",
                encoding="utf-8",
            ) as f:

                f.write(content)

            return Result.ok(
                message=f"تم تحديث الملف: {filepath}",
            )

        except Exception as e:

            return Result.fail(
                message=str(e),
            )