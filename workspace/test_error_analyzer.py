from services.error_analyzer import ErrorAnalyzer
from tools.file_tools import FileTools
from tools.terminal_tools import TerminalTools
from tools.python_tools import PythonTools


analyzer = ErrorAnalyzer(
    file_tools=FileTools(),
    terminal_tools=TerminalTools(),
    python_tools=PythonTools(),
)


print("=" * 60)
print("Analyze Exception")
print("=" * 60)

try:
    x = 10 / 0
except Exception as ex:
    result = analyzer.analyze_exception(ex)

    print(result)
    print(result.success)
    print(result.metadata["type"])


print()
print("=" * 60)
print("Analyze Success Result")
print("=" * 60)

ok = analyzer.file_tools.exists(".")

result = analyzer.analyze_result(ok)

print(result)
print(result.success)
print(result.data)


print()
print("=" * 60)
print("Analyze Failed Result")
print("=" * 60)

failed = analyzer.file_tools.read_text("file_not_found.txt")

result = analyzer.analyze_result(failed)

print(result)
print(result.success)
print(result.data)


print()
print("=" * 60)
print("Summary")
print("=" * 60)

summary = analyzer.summarize(failed)

print(summary)
print(summary.success)
print(summary.data)