from core.process import ProcessRunner

runner = ProcessRunner()

print("=" * 60)
print("Python Version")
print("=" * 60)

result = runner.run(["python", "--version"])

print(result)
print(result.success)
print(result.data)

print("\n" + "=" * 60)
print("Invalid Command")
print("=" * 60)

result = runner.run(["command_that_does_not_exist"])

print(result)
print(result.success)
print(result.errors)