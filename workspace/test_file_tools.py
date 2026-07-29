from tools.file_tools import FileTools

tools = FileTools()

result = tools.write_text(
    "workspace/demo.txt",
    "Hello World"
)

print(result)

print(tools.exists("workspace/demo.txt").data)

print(tools.read_text("workspace/demo.txt").data)

print(tools.file_size("workspace/demo.txt").data)

print(tools.list_files("workspace").metadata)

print(tools.delete("workspace/demo.txt"))

print(tools.exists("workspace/demo.txt").data)