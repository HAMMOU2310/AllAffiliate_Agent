from pathlib import Path

from tools.python_tools import PythonTools

python = PythonTools()


def title(text: str):
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


# -------------------------------------------------------------------
# Python Executable
# -------------------------------------------------------------------

title("Python Executable")

result = python.executable()

print(result)
print(result.success)
print(result.data)


# -------------------------------------------------------------------
# Python Version
# -------------------------------------------------------------------

title("Python Version")

result = python.python_version()

print(result)
print(result.success)
print(result.data)


# -------------------------------------------------------------------
# Execute Inline Code
# -------------------------------------------------------------------

title("Run Python Code")

result = python.run_code(
    "print('Hello from PythonTools')"
)

print(result)
print(result.success)
print(result.data)


# -------------------------------------------------------------------
# Execute Inline Code With Math
# -------------------------------------------------------------------

title("Run Python Math")

result = python.run_code(
    "print(5 * 9)"
)

print(result)
print(result.data)


# -------------------------------------------------------------------
# Execute Module
# -------------------------------------------------------------------

title("Run Module")

result = python.run_module(
    "platform"
)

print(result)
print(result.success)
print(result.metadata["return_code"])


# -------------------------------------------------------------------
# Create Temporary Script
# -------------------------------------------------------------------

title("Create Test Script")

script = Path("workspace/demo_script.py")

script.write_text(
    """
print("Demo Script")
print(100 + 200)
""".strip(),
    encoding="utf-8"
)

print(script.exists())


# -------------------------------------------------------------------
# Execute Script
# -------------------------------------------------------------------

title("Run Script")

result = python.run_script(script)

print(result)
print(result.success)
print(result.data)


# -------------------------------------------------------------------
# Delete Script
# -------------------------------------------------------------------

title("Cleanup")

script.unlink()

print(script.exists())


# -------------------------------------------------------------------
# Invalid Script
# -------------------------------------------------------------------

title("Invalid Script")

result = python.run_script(
    "workspace/not_found.py"
)

print(result)
print(result.success)

if result.metadata:
    print(result.metadata)

if result.errors:
    print(result.errors)


# -------------------------------------------------------------------
# Finished
# -------------------------------------------------------------------

title("Finished")

print("PythonTools test completed.")