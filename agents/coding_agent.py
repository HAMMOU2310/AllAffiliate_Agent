import subprocess
import json
import os

class CodingAgent:
    def __init__(self):
        self.name = "CodingAgent"
        self.version = "1.0.0"

    def process_task(self, task_type: str, payload: dict):
        """معالجة المهام الموجهة إلى وكيل البرمجة بناءً على نوع المهمة."""
        if task_type == "git_status":
            return self.check_git_status(payload.get("repo_path", "."))
        elif task_type == "inspect_json":
            return self.inspect_json_file(payload.get("file_path"))
        else:
            return {"status": "error", "message": f"نوع المهمة '{task_type}' غير مدعوم."}

    def check_git_status(self, repo_path: str):
        """فحص حالة مستودع Git."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return {"git_status": result.stdout}
        except Exception as e:
            return {"git_status_error": str(e)}

    def inspect_json_file(self, file_path: str):
        """فحص وقراءة ملف JSON للتأكد من سلامة هيكله."""
        try:
            if not file_path or not os.path.exists(file_path):
                return {"status": "error", "message": "ملف الـ JSON غير موجود أو المسار غير صحيح."}
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {"status": "success", "data": data}
        except json.JSONDecodeError as jde:
            return {"status": "error", "message": f"خطأ في تنسيق ملف الـ JSON: {str(jde)}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}