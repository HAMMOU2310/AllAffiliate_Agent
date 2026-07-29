from tools.terminal_tools import TerminalTools

terminal = TerminalTools()


print("=" * 60)
print("Current Directory")
print("=" * 60)

result = terminal.current_directory()
print(result)
print(result.data)


print("\n" + "=" * 60)
print("Python Exists")
print("=" * 60)

result = terminal.command_exists("python")
print(result)
print(result.data)


print("\n" + "=" * 60)
print("PowerShell Test")
print("=" * 60)

result = terminal.run_powershell(
    "Write-Output 'Hello PowerShell'"
)

print(result)
print(result.data)


print("\n" + "=" * 60)
print("CMD Test")
print("=" * 60)

result = terminal.run_cmd(
    "echo Hello CMD"
)

print(result)
print(result.data)


print("\n" + "=" * 60)
print("Python Version")
print("=" * 60)

result = terminal.run(
    ["python", "--version"]
)

print(result)
print(result.data)