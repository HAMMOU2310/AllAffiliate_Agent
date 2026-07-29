from pathlib import Path

from services.python_runner import PythonRunner
from tools.file_tools import FileTools
from tools.python_tools import PythonTools
from tools.terminal_tools import TerminalTools


runner = PythonRunner(
    file_tools=FileTools(),
    terminal_tools=TerminalTools(),
    python_tools=PythonTools(),
)

print("=" * 60)
print("Python Executable")
print("=" * 60)

result = runner.python_executable()

print(result)
print(result.success)
print(result.data)

print("\n" + "=" * 60)
print("Python Version")
print("=" * 60)

result = runner.python_version()

print(result)
print(result.success)
print(result.data)

print("\n" + "=" * 60)
print("Run Code")
print("=" * 60)

result = runner.run_code(
    "print('Hello from PythonRunner')"
)

print(result)
print(result.success)
print(result.data)

print("\n" + "=" * 60)
print("Create Demo Script")
print("=" * 60)

script = Path("workspace/demo_runner.py")
script.write_text(
    "print('Runner OK')",
    encoding="utf-8",
)

print(script.exists())

print("\n" + "=" * 60)
print("Run Script")
print("=" * 60)

result = runner.run_script(script)

print(result)
print(result.success)
print(result.data)

print("\n" + "=" * 60)
print("Run Module")
print("=" * 60)

result = runner.run_module("workspace.demo_module")

print(result)
print(result.success)
print(result.metadata["return_code"])