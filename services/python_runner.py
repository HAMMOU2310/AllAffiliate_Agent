from pathlib import Path
import subprocess

from core.result import Result


class PythonRunner:
    """
    مسؤول عن تشغيل ملفات Python.
    """

    def run_file(self, file_path: str) -> Result:

        path = Path(file_path)

        if not path.exists():
            return Result.fail(
                message=f"الملف غير موجود: {file_path}"
            )

        if path.suffix != ".py":
            return Result.fail(
                message="الملف ليس Python."
            )

        try:

            process = subprocess.run(
                ["python", str(path)],
                capture_output=True,
                text=True,
            )

            return Result.ok(
                message="تم تشغيل الملف.",
                data={
                    "stdout": process.stdout,
                    "stderr": process.stderr,
                    "returncode": process.returncode,
                },
            )

        except Exception as e:

            return Result.fail(
                message=str(e)
            )