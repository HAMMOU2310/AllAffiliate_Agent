from pathlib import Path

from services.code_writer import CodeWriter
from tools.file_tools import FileTools
from tools.python_tools import PythonTools
from tools.terminal_tools import TerminalTools


writer = CodeWriter(
    file_tools=FileTools(),
    terminal_tools=TerminalTools(),
    python_tools=PythonTools(),
)

file = Path("workspace/example.py")

print("=" * 60)
print("Create")
print("=" * 60)

result = writer.create_python_file(
    file,
    "print('Hello')\n",
)

print(result)
print(result.success)

print("=" * 60)
print("Append")
print("=" * 60)

result = writer.append_to_file(
    file,
    "print('World')\n",
)

print(result)
print(result.success)

print("=" * 60)
print("Overwrite")
print("=" * 60)

result = writer.overwrite_file(
    file,
    "print('Replaced')\n",
)

print(result)
print(result.success)

print("=" * 60)
print("Content")
print("=" * 60)

print(file.read_text(encoding="utf-8"))