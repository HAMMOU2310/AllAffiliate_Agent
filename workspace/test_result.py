from core.result import Result

ok = Result.ok(
    data={"name": "Ali"},
    message="Success"
)

print(ok)
print(ok.success)
print(ok.failed)
print(ok.data)

fail = Result.fail(
    message="Something went wrong",
    errors=["Invalid path"]
)

print(fail)
print(fail.success)
print(fail.failed)
print(fail.errors)

print(bool(ok))
print(bool(fail))