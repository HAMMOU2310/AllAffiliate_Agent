from pathlib import Path

from services.project_manager import ProjectManager
from tools.file_tools import FileTools
from tools.python_tools import PythonTools
from tools.terminal_tools import TerminalTools


manager = ProjectManager(
    file_tools=FileTools(),
    terminal_tools=TerminalTools(),
    python_tools=PythonTools(),
)

project = Path("workspace/demo_project")


print("=" * 60)
print("Create Project")
print("=" * 60)

result = manager.create_project(project)

print(result)
print(result.success)


print("\n" + "=" * 60)
print("Project Exists")
print("=" * 60)

result = manager.project_exists(project)

print(result)
print(result.data)


print("\n" + "=" * 60)
print("Project Info")
print("=" * 60)

result = manager.project_info(project)

print(result)
print(result.data)