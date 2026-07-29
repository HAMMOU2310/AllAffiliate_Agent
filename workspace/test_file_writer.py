from core.file_writer import FileWriter

writer = FileWriter()

path = writer.write(
    "workspace/hello.txt",
    "Hello Builder!"
)

print(path)
print(path.exists())
print(path.read_text())